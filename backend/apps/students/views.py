"""
Views for Students app.
"""
import csv
import io
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse

from .models import Student
from .serializers import StudentSerializer, StudentListSerializer


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student model.

    Provides CRUD operations and custom actions:
    - GET /students/ - List all students
    - POST /students/ - Create a student
    - GET /students/{id}/ - Retrieve a student
    - PUT/PATCH /students/{id}/ - Update a student
    - DELETE /students/{id}/ - Delete a student
    - GET /students/{id}/predictions/ - Get student predictions
    - GET /students/{id}/grades/ - Get student grades
    - GET /students/{id}/attendance/ - Get student attendance
    - GET /students/at-risk/ - Get at-risk students
    """
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['program', 'session', 'risk_level', 'status']
    search_fields = ['matricule', 'first_name', 'last_name', 'email']
    ordering_fields = ['last_name', 'first_name', 'created_at', 'risk_score']
    ordering = ['last_name', 'first_name']

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return StudentListSerializer
        return StudentSerializer

    def get_queryset(self):
        """Optimize queryset with select_related and prefetch_related."""
        queryset = Student.objects.select_related(
            'program',
            'session'
        ).prefetch_related(
            'predictions',
            'grades',
            'attendances'
        )
        return queryset

    @action(detail=True, methods=['get'])
    def predictions(self, request, pk=None):
        """
        Get all predictions for a specific student.

        GET /students/{id}/predictions/
        """
        student = self.get_object()

        # Import here to avoid circular imports
        from apps.predictions.models import Prediction
        from apps.predictions.serializers import PredictionSerializer

        predictions = Prediction.objects.filter(
            student=student
        ).select_related('model_version').order_by('-created_at')

        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def grades(self, request, pk=None):
        """
        Get all grades for a specific student.

        GET /students/{id}/grades/
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
        """
        at_risk_students = self.get_queryset().filter(
            risk_level__in=['medium', 'high']
        ).order_by('-risk_score')

        serializer = self.get_serializer(at_risk_students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export all students to CSV format.

        GET /students/export-csv/
        """
        students = self.get_queryset()
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        
        # BOM UTF-8 pour Excel
        response.write('\ufeff')
        
        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'Matricule', 'Prénom', 'Nom', 'Email', 'Téléphone',
            'Date de naissance', 'Programme', 'Session', 'Statut',
            'Niveau de risque', 'Score de risque'
        ])
        
        for student in students:
            writer.writerow([
                student.matricule,
                student.first_name,
                student.last_name,
                student.email,
                student.phone or '',
                student.date_of_birth.strftime('%Y-%m-%d') if student.date_of_birth else '',
                student.program.name if student.program else '',
                student.session.name if student.session else '',
                student.get_status_display(),
                student.get_risk_level_display() if student.risk_level else '',
                str(student.risk_score) if student.risk_score else ''
            ])
        
        return response

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def import_csv(self, request):
        """
        Import students from CSV file.

        POST /students/import-csv/
        
        Expected CSV format (semicolon-separated, UTF-8):
        Matricule;Prénom;Nom;Email;Téléphone;Date de naissance;Programme (code);Session (name);Statut
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
            # Décoder le fichier
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string, delimiter=';')
            
            created = 0
            updated = 0
            errors = []
            
            from apps.programs.models import Program
            from apps.sessions.models import Session
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Rechercher programme et session
                    program = None
                    session = None
                    
                    program_code = row.get('Programme (code)', '').strip()
                    if program_code:
                        program = Program.objects.filter(code=program_code).first()
                        if not program:
                            errors.append(f"Ligne {row_num}: Programme '{program_code}' non trouvé")
                            continue
                    
                    session_name = row.get('Session (name)', '').strip()
                    if session_name:
                        session = Session.objects.filter(name=session_name).first()
                        if not session:
                            errors.append(f"Ligne {row_num}: Session '{session_name}' non trouvée")
                            continue
                    
                    matricule = row.get('Matricule', '').strip()
                    if not matricule:
                        errors.append(f"Ligne {row_num}: Matricule requis")
                        continue
                    
                    # Mapper le statut
                    status_map = {
                        'Actif': 'active',
                        'Inactif': 'inactive',
                        'Diplômé': 'graduated',
                        'active': 'active',
                        'inactive': 'inactive',
                        'graduated': 'graduated'
                    }
                    status_value = status_map.get(
                        row.get('Statut', 'Actif').strip(),
                        'active'
                    )
                    
                    # Créer ou mettre à jour
                    student, was_created = Student.objects.update_or_create(
                        matricule=matricule,
                        defaults={
                            'first_name': row.get('Prénom', '').strip(),
                            'last_name': row.get('Nom', '').strip(),
                            'email': row.get('Email', '').strip(),
                            'phone': row.get('Téléphone', '').strip() or None,
                            'date_of_birth': row.get('Date de naissance', '').strip() or None,
                            'program': program,
                            'session': session,
                            'status': status_value,
                        }
                    )
                    
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                        
                except Exception as e:
                    errors.append(f"Ligne {row_num}: {str(e)}")
            
            return Response({
                'success': True,
                'message': f'{created} étudiant(s) créé(s), {updated} mis à jour.',
                'created': created,
                'updated': updated,
                'errors': errors[:20] if errors else []  # Limiter à 20 erreurs
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du traitement du fichier: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
