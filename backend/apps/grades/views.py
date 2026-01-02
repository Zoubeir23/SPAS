"""
Views for Grades app.
"""
import csv
import io
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count
from django.db import transaction
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation

from .models import Grade
from .serializers import GradeSerializer


class GradeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Grade model.

    Provides CRUD operations and custom actions:
    - GET /grades/ - List all grades
    - POST /grades/ - Create a grade
    - GET /grades/{id}/ - Retrieve a grade
    - PUT/PATCH /grades/{id}/ - Update a grade
    - DELETE /grades/{id}/ - Delete a grade
    - GET /grades/student/{student_id}/ - Get grades for a student
    - POST /grades/bulk-create/ - Create multiple grades at once
    """
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'subject', 'session', 'type']
    search_fields = ['student__first_name', 'student__last_name', 'student__matricule']
    ordering_fields = ['date', 'value', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        """Optimize queryset with select_related."""
        queryset = Grade.objects.select_related(
            'student',
            'subject',
            'session'
        )
        return queryset

    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)')
    def student_grades(self, request, student_id=None):
        """
        Get all grades for a specific student.

        GET /grades/student/{student_id}/
        """
        grades = self.get_queryset().filter(
            student_id=student_id
        ).order_by('-date')

        serializer = self.get_serializer(grades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """
        Create multiple grades at once.

        POST /grades/bulk-create/
        Body: {
            "grades": [
                {
                    "student": 1,
                    "subject": 1,
                    "session": 1,
                    "value": 85.5,
                    "max_value": 100,
                    "type": "exam",
                    "date": "2024-01-15"
                },
                ...
            ]
        }
        """
        grades_data = request.data.get('grades', [])

        if not grades_data:
            return Response(
                {'error': 'No grades data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_grades = []
        errors = []

        with transaction.atomic():
            for idx, grade_data in enumerate(grades_data):
                serializer = self.get_serializer(data=grade_data)
                if serializer.is_valid():
                    grade = serializer.save()
                    created_grades.append(grade)
                else:
                    errors.append({
                        'index': idx,
                        'data': grade_data,
                        'errors': serializer.errors
                    })

            if errors:
                # Rollback transaction if there are errors
                transaction.set_rollback(True)
                return Response(
                    {
                        'error': 'Some grades could not be created',
                        'errors': errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(created_grades, many=True)
        return Response(
            {
                'success': True,
                'message': f'{len(created_grades)} grades created successfully',
                'grades': serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get grade statistics.

        GET /grades/statistics/
        """
        queryset = self.get_queryset()

        # Filter by query parameters if provided
        student_id = request.query_params.get('student')
        subject_id = request.query_params.get('subject')
        session_id = request.query_params.get('session')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if session_id:
            queryset = queryset.filter(session_id=session_id)

        stats = queryset.aggregate(
            total_grades=Count('id'),
            average_grade=Avg('value'),
        )

        # Add grade distribution
        grade_distribution = {
            'A': queryset.filter(value__gte=90).count(),
            'B': queryset.filter(value__gte=80, value__lt=90).count(),
            'C': queryset.filter(value__gte=70, value__lt=80).count(),
            'D': queryset.filter(value__gte=60, value__lt=70).count(),
            'F': queryset.filter(value__lt=60).count(),
        }

        return Response({
            'statistics': stats,
            'distribution': grade_distribution
        })

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export grades to CSV format.

        GET /grades/export-csv/
        Query params: student, subject, session (optional filters)
        """
        queryset = self.get_queryset()
        
        # Apply filters
        student_id = request.query_params.get('student')
        subject_id = request.query_params.get('subject')
        session_id = request.query_params.get('session')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="notes.csv"'
        
        # BOM UTF-8 pour Excel
        response.write('\ufeff')
        
        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'Matricule', 'Étudiant', 'Matière', 'Session',
            'Type', 'Note', 'Note maximale', 'Date'
        ])
        
        for grade in queryset.order_by('student__last_name', 'subject__name', '-date'):
            writer.writerow([
                grade.student.matricule,
                f"{grade.student.last_name} {grade.student.first_name}",
                grade.subject.name if grade.subject else '',
                grade.session.name if grade.session else '',
                grade.get_type_display(),
                str(grade.value),
                str(grade.max_value),
                grade.date.strftime('%Y-%m-%d') if grade.date else ''
            ])
        
        return response

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def import_csv(self, request):
        """
        Import grades from CSV file.

        POST /grades/import-csv/
        
        Expected CSV format (semicolon-separated, UTF-8):
        Matricule;Matière (code);Session (name);Type;Note;Note maximale;Date
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'Aucun fichier fourni. Utilisez le champ "file".'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = request.FILES['file']
        
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'Le fichier doit être au format CSV.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string, delimiter=';')
            
            created = 0
            errors = []
            
            from apps.students.models import Student
            from apps.programs.models import Subject
            from apps.sessions.models import Session
            
            # Mapper les types de notes
            type_map = {
                'Examen': 'exam',
                'Devoir': 'assignment',
                'Projet': 'project',
                'Participation': 'participation',
                'exam': 'exam',
                'assignment': 'assignment',
                'project': 'project',
                'participation': 'participation'
            }
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):
                    try:
                        matricule = row.get('Matricule', '').strip()
                        student = Student.objects.filter(matricule=matricule).first()
                        if not student:
                            errors.append(f"Ligne {row_num}: Étudiant '{matricule}' non trouvé")
                            continue
                        
                        subject_code = row.get('Matière (code)', '').strip()
                        subject = Subject.objects.filter(code=subject_code).first()
                        if not subject:
                            errors.append(f"Ligne {row_num}: Matière '{subject_code}' non trouvée")
                            continue
                        
                        session_name = row.get('Session (name)', '').strip()
                        session = Session.objects.filter(name=session_name).first()
                        if not session:
                            errors.append(f"Ligne {row_num}: Session '{session_name}' non trouvée")
                            continue
                        
                        try:
                            value = Decimal(row.get('Note', '0').strip().replace(',', '.'))
                            max_value = Decimal(row.get('Note maximale', '20').strip().replace(',', '.'))
                        except InvalidOperation:
                            errors.append(f"Ligne {row_num}: Note invalide")
                            continue
                        
                        grade_type = type_map.get(
                            row.get('Type', 'exam').strip(),
                            'exam'
                        )
                        
                        grade_date = row.get('Date', '').strip()
                        
                        Grade.objects.create(
                            student=student,
                            subject=subject,
                            session=session,
                            value=value,
                            max_value=max_value,
                            type=grade_type,
                            date=grade_date if grade_date else None
                        )
                        created += 1
                        
                    except Exception as e:
                        errors.append(f"Ligne {row_num}: {str(e)}")
            
            return Response({
                'success': True,
                'message': f'{created} note(s) créée(s).',
                'created': created,
                'errors': errors[:20] if errors else []
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du traitement du fichier: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
