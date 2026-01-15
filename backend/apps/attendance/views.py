"""
Views for Attendance app.

Permissions par rôle:
- ADMIN: Full CRUD access
- DS: Full CRUD access
- TEACHER: Create/Update attendance for their students
- PEDAGOGICAL: Read-only access
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg
from django.db import transaction

from .models import Attendance
from .serializers import AttendanceSerializer
from apps.core.mixins import RoleBasedPermissionMixin, AuditLogMixin
from apps.core.permissions import (
    IsAdmin, IsDSOrAdmin, IsTeacherOrAdmin, IsPedagogicalOrAbove
)


class AttendanceViewSet(RoleBasedPermissionMixin, AuditLogMixin, viewsets.ModelViewSet):
    """
    ViewSet for Attendance model.

    Provides CRUD operations and custom actions:
    - GET /attendance/ - List all attendance records
    - POST /attendance/ - Create an attendance record (Teacher/DS/Admin)
    - GET /attendance/{id}/ - Retrieve an attendance record
    - PUT/PATCH /attendance/{id}/ - Update an attendance record (Teacher/DS/Admin)
    - DELETE /attendance/{id}/ - Delete an attendance record (Admin only)
    - GET /attendance/student/{student_id}/ - Get attendance for a student
    - POST /attendance/bulk-create/ - Create multiple attendance records (Teacher/DS/Admin)
    - GET /attendance/statistics/ - Get attendance statistics
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    # Role-based permissions per action
    permission_classes_by_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsAuthenticated, IsTeacherOrAdmin],
        'update': [IsAuthenticated, IsTeacherOrAdmin],
        'partial_update': [IsAuthenticated, IsTeacherOrAdmin],
        'destroy': [IsAuthenticated, IsAdmin],
        'bulk_create': [IsAuthenticated, IsTeacherOrAdmin],
        'statistics': [IsAuthenticated],
        'low_attendance': [IsAuthenticated, IsPedagogicalOrAbove],
    }
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'subject', 'status', 'date']
    search_fields = ['student__first_name', 'student__last_name', 'student__matricule']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        """Optimize queryset with select_related."""
        queryset = Attendance.objects.select_related(
            'student',
            'subject'
        )
        return queryset

    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)')
    def student_attendance(self, request, student_id=None):
        """
        Get all attendance records for a specific student.

        GET /attendance/student/{student_id}/
        """
        attendance = self.get_queryset().filter(
            student_id=student_id
        ).order_by('-date')

        serializer = self.get_serializer(attendance, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """
        Create multiple attendance records at once.

        POST /attendance/bulk-create/
        Body: {
            "records": [
                {
                    "student": 1,
                    "subject": 1,
                    "date": "2024-01-15",
                    "status": "present"
                },
                ...
            ]
        }
        """
        records_data = request.data.get('records', [])

        if not records_data:
            return Response(
                {'error': 'No attendance records provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_records = []
        errors = []

        with transaction.atomic():
            for idx, record_data in enumerate(records_data):
                serializer = self.get_serializer(data=record_data)
                if serializer.is_valid():
                    record = serializer.save()
                    created_records.append(record)
                else:
                    errors.append({
                        'index': idx,
                        'data': record_data,
                        'errors': serializer.errors
                    })

            if errors:
                # Rollback transaction if there are errors
                transaction.set_rollback(True)
                return Response(
                    {
                        'error': 'Some attendance records could not be created',
                        'errors': errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(created_records, many=True)
        return Response(
            {
                'success': True,
                'message': f'{len(created_records)} attendance records created successfully',
                'records': serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get attendance statistics.

        GET /attendance/statistics/
        """
        queryset = self.get_queryset()

        # Filter by query parameters if provided
        student_id = request.query_params.get('student')
        subject_id = request.query_params.get('subject')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        total_records = queryset.count()

        stats = queryset.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late')),
            excused=Count('id', filter=Q(status='excused')),
        )

        # Calculate attendance rate
        if total_records > 0:
            attendance_rate = (stats['present'] / total_records) * 100
        else:
            attendance_rate = 0

        return Response({
            'statistics': stats,
            'attendance_rate': round(attendance_rate, 2),
            'total_records': total_records
        })

    @action(detail=False, methods=['get'])
    def low_attendance(self, request):
        """
        Get students with low attendance rates.

        GET /attendance/low-attendance/?threshold=70
        """
        threshold = float(request.query_params.get('threshold', 70))

        # Import here to avoid circular imports
        from apps.students.models import Student
        from apps.students.serializers import StudentListSerializer

        # Get all active students
        students = Student.objects.filter(status='active')

        low_attendance_students = []

        for student in students:
            # Get attendance records for this student
            student_attendance = Attendance.objects.filter(student=student)
            total = student_attendance.count()

            if total > 0:
                present = student_attendance.filter(status='present').count()
                rate = (present / total) * 100

                if rate < threshold:
                    student_data = StudentListSerializer(student).data
                    student_data['attendance_rate'] = round(rate, 2)
                    student_data['total_records'] = total
                    low_attendance_students.append(student_data)

        return Response({
            'threshold': threshold,
            'count': len(low_attendance_students),
            'students': low_attendance_students
        })
