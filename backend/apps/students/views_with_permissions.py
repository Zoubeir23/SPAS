"""
Students ViewSet with comprehensive permissions and security.

This is an example of how to apply the core permissions system to a ViewSet.
To use this, rename this file to views.py or copy the code to views.py.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import (
    RoleBasedPermissionMixin,
    AuditLogMixin,
    QuerySetFilterMixin,
    SoftDeleteMixin
)
from apps.core.permissions import (
    IsAdmin,
    IsTeacherOrAdmin,
    IsPedagogicalOrAbove,
    CanManageStudents,
    CanViewPredictions
)
from apps.core.throttling import DataExportThrottle

from .models import Student
from .serializers import StudentSerializer, StudentListSerializer


class StudentViewSet(
    RoleBasedPermissionMixin,
    AuditLogMixin,
    QuerySetFilterMixin,
    SoftDeleteMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet for Student model with role-based permissions.

    Provides CRUD operations and custom actions:
    - GET /students/ - List all students (Pedagogical+)
    - POST /students/ - Create a student (Teacher+)
    - GET /students/{id}/ - Retrieve a student (Pedagogical+)
    - PUT/PATCH /students/{id}/ - Update a student (Teacher+)
    - DELETE /students/{id}/ - Soft delete a student (Admin only)
    - POST /students/{id}/restore/ - Restore deleted student (Admin only)
    - DELETE /students/{id}/hard-delete/ - Permanently delete (Admin only)
    - GET /students/{id}/predictions/ - Get student predictions
    - GET /students/{id}/grades/ - Get student grades
    - GET /students/{id}/attendance/ - Get student attendance
    - GET /students/at-risk/ - Get at-risk students
    - GET /students/export/ - Export students data

    Permissions:
    - ADMIN: Full access to all students
    - DS: Full access to all students
    - PEDAGOGICAL: Read-only access to all students
    - TEACHER: Manage only their own students

    Audit Logging:
    All create, update, and delete operations are automatically logged.
    """
    queryset = Student.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['program', 'session', 'risk_level', 'status']
    search_fields = ['matricule', 'first_name', 'last_name', 'email']
    ordering_fields = ['last_name', 'first_name', 'created_at', 'risk_score']
    ordering = ['last_name', 'first_name']

    # Field used to filter students for teachers
    filter_field = 'teacher'

    # Permissions by action
    permission_classes_by_action = {
        'list': [IsPedagogicalOrAbove],
        'retrieve': [IsPedagogicalOrAbove],
        'create': [IsTeacherOrAdmin],
        'update': [CanManageStudents],
        'partial_update': [CanManageStudents],
        'destroy': [IsAdmin],
        'restore': [IsAdmin],
        'hard_delete': [IsAdmin],
        'predictions': [CanViewPredictions],
        'grades': [IsPedagogicalOrAbove],
        'attendance': [IsPedagogicalOrAbove],
        'at_risk': [IsPedagogicalOrAbove],
        'export': [IsPedagogicalOrAbove],
    }

    # Audit logging configuration
    audit_log_actions = ['create', 'update', 'partial_update', 'destroy', 'export']
    audit_log_changes = True

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return StudentListSerializer
        return StudentSerializer

    def get_queryset(self):
        """
        Optimize queryset with select_related and prefetch_related.
        Also filters by user role (handled by QuerySetFilterMixin).
        """
        queryset = Student.objects.select_related(
            'program',
            'session'
        ).prefetch_related(
            'predictions',
            'grades',
            'attendances'
        )

        # QuerySetFilterMixin will filter this based on user role
        return super().get_queryset()

    def get_queryset_for_teacher(self, queryset):
        """
        Teachers see only their assigned students.

        Override this method to customize filtering logic.
        """
        user = self.request.user

        # Option 1: If students have a direct teacher field
        if hasattr(Student, 'teacher'):
            return queryset.filter(teacher=user)

        # Option 2: If students are linked through sessions/classes
        # Get all sessions where this teacher teaches
        teacher_sessions = user.teaching_sessions.all()

        # Filter students enrolled in those sessions
        return queryset.filter(session__in=teacher_sessions)

    def perform_create(self, serializer):
        """
        Override to set the teacher field when creating a student.
        """
        # If user is a teacher, automatically assign them as the teacher
        if self.request.user.is_teacher():
            # Assuming the Student model has a teacher field
            if hasattr(Student, 'teacher'):
                serializer.save(teacher=self.request.user)
            else:
                serializer.save()
        else:
            serializer.save()

        # AuditLogMixin will automatically log this action

    @action(detail=True, methods=['get'])
    def predictions(self, request, pk=None):
        """
        Get all predictions for a specific student.

        GET /students/{id}/predictions/

        Permissions: CanViewPredictions
        - Teachers can view predictions for their students
        - Pedagogical+ can view all predictions
        """
        student = self.get_object()

        # Import here to avoid circular imports
        from apps.predictions.models import Prediction
        from apps.predictions.serializers import PredictionSerializer

        predictions = Prediction.objects.filter(
            student=student
        ).select_related('model_version').order_by('-created_at')

        serializer = PredictionSerializer(predictions, many=True)

        # Log viewing predictions as it's sensitive data
        self.create_audit_log(
            action_type='view',
            instance=student,
            extra_data={'viewed': 'predictions'}
        )

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        """
        Get all grades for a specific student.

        GET /students/{id}/grades/

        Permissions: IsPedagogicalOrAbove
        """
        student = self.get_object()

        # Import here to avoid circular imports
        from apps.grades.models import Grade
        from apps.grades.serializers import GradeSerializer

        grades = Grade.objects.filter(
            student=student
        ).select_related('subject', 'session').order_by('-date')

        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """
        Get all attendance records for a specific student.

        GET /students/{id}/attendance/

        Permissions: IsPedagogicalOrAbove
        """
        student = self.get_object()

        # Import here to avoid circular imports
        from apps.attendance.models import Attendance
        from apps.attendance.serializers import AttendanceSerializer

        attendance = Attendance.objects.filter(
            student=student
        ).select_related('subject').order_by('-date')

        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def at_risk(self, request):
        """
        Get all students at risk (medium, high risk levels).

        GET /students/at-risk/

        Permissions: IsPedagogicalOrAbove

        Returns students filtered by user role:
        - Teachers see their at-risk students
        - Pedagogical+ see all at-risk students
        """
        # get_queryset() already filters by role
        at_risk_students = self.get_queryset().filter(
            risk_level__in=['medium', 'high']
        ).order_by('-risk_score')

        # Use pagination
        page = self.paginate_queryset(at_risk_students)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(at_risk_students, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        throttle_classes=[DataExportThrottle]
    )
    def export(self, request):
        """
        Export students data to CSV.

        GET /students/export/?format=csv

        Permissions: IsPedagogicalOrAbove
        Throttling: DataExportThrottle (limited requests per hour)

        Query parameters:
        - format: csv or json (default: csv)
        - filters: Same as list endpoint

        Returns:
        - CSV file with student data
        """
        import csv
        from django.http import HttpResponse
        from datetime import datetime

        # Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())

        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="students_{timestamp}.csv"'

        # Create CSV writer
        writer = csv.writer(response)

        # Write header
        writer.writerow([
            'Matricule',
            'Prénom',
            'Nom',
            'Email',
            'Programme',
            'Session',
            'Niveau de Risque',
            'Score de Risque',
            'Statut',
            'Date de Création'
        ])

        # Write data rows
        for student in queryset:
            writer.writerow([
                student.matricule,
                student.first_name,
                student.last_name,
                student.email,
                student.program.name if student.program else '',
                student.session.name if student.session else '',
                student.get_risk_level_display(),
                student.risk_score or '',
                student.get_status_display(),
                student.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        # Log the export action
        self.create_audit_log(
            action_type='export',
            instance=None,
            extra_data={
                'format': 'csv',
                'count': queryset.count()
            }
        )

        return response

    @action(detail=True, methods=['post'])
    def assign_teacher(self, request, pk=None):
        """
        Assign a teacher to a student.

        POST /students/{id}/assign_teacher/

        Permissions: IsAdmin or IsDSOrAdmin

        Body:
        {
            "teacher_id": 123
        }
        """
        from apps.users.models import User

        student = self.get_object()
        teacher_id = request.data.get('teacher_id')

        if not teacher_id:
            return Response(
                {'error': 'teacher_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            teacher = User.objects.get(id=teacher_id, role=User.Role.TEACHER)
        except User.DoesNotExist:
            return Response(
                {'error': 'Enseignant non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Assign teacher (if the field exists)
        if hasattr(student, 'teacher'):
            old_teacher = student.teacher
            student.teacher = teacher
            student.save()

            # Log the change
            self.create_audit_log(
                action_type='update',
                instance=student,
                changes={
                    'before': {'teacher_id': old_teacher.id if old_teacher else None},
                    'after': {'teacher_id': teacher.id}
                }
            )

            return Response({
                'status': 'success',
                'message': f'Enseignant {teacher.get_full_name()} assigné à {student.get_full_name()}'
            })
        else:
            return Response(
                {'error': 'Le modèle Student ne supporte pas l\'assignation d\'enseignant'},
                status=status.HTTP_400_BAD_REQUEST
            )
