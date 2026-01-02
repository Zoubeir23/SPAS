"""
Views for Prediction app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Max, Subquery, Q

from .models import Prediction
from .serializers import PredictionSerializer, PredictionListSerializer
from apps.ml.services import DropoutRiskPredictor, calculate_student_features_from_db
from apps.ml.models import MLModel


class PredictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Prediction model.

    Provides CRUD operations and custom actions:
    - GET /predictions/ - List all predictions
    - POST /predictions/ - Create a prediction
    - GET /predictions/{id}/ - Retrieve a prediction
    - PUT/PATCH /predictions/{id}/ - Update a prediction
    - DELETE /predictions/{id}/ - Delete a prediction
    - GET /predictions/student/{student_id}/ - Get predictions for a student
    - GET /predictions/statistics/ - Get prediction statistics
    - GET /predictions/at_risk/ - Get high-risk predictions
    """
    queryset = Prediction.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'risk_level', 'model_version']
    search_fields = ['student__first_name', 'student__last_name', 'student__matricule']
    ordering_fields = ['risk_score', 'predicted_success_rate', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return PredictionListSerializer
        return PredictionSerializer

    def get_queryset(self):
        """Optimize queryset with select_related."""
        queryset = Prediction.objects.select_related(
            'student',
            'model_version'
        )

        # Filter by student
        student_id = self.request.query_params.get('student', None)
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        # Filter by risk level
        risk_level = self.request.query_params.get('risk_level', None)
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)

        return queryset

    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)')
    def student_predictions(self, request, student_id=None):
        """
        Get all predictions for a specific student.

        GET /predictions/student/{student_id}/
        """
        predictions = self.get_queryset().filter(
            student_id=student_id
        ).order_by('-created_at')

        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def at_risk(self, request):
        """
        Get students at high risk (risk level HIGH or CRITICAL).

        GET /predictions/at_risk/
        """
        high_risk = self.get_queryset().filter(
            risk_level__in=[Prediction.RiskLevel.HIGH, Prediction.RiskLevel.CRITICAL]
        ).order_by('-risk_score')

        serializer = self.get_serializer(high_risk, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get prediction statistics.

        GET /predictions/statistics/
        """
        queryset = self.get_queryset()

        # Filter by query parameters if provided
        student_id = request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        stats = queryset.aggregate(
            total_predictions=Count('id'),
            average_risk_score=Avg('risk_score'),
            average_success_rate=Avg('predicted_success_rate'),
        )

        # Add risk level distribution
        risk_distribution = {
            'low': queryset.filter(risk_level=Prediction.RiskLevel.LOW).count(),
            'medium': queryset.filter(risk_level=Prediction.RiskLevel.MEDIUM).count(),
            'high': queryset.filter(risk_level=Prediction.RiskLevel.HIGH).count(),
            'critical': queryset.filter(risk_level=Prediction.RiskLevel.CRITICAL).count(),
        }

        return Response({
            'statistics': stats,
            'risk_distribution': risk_distribution
        })

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Get the latest prediction for each student.

        GET /predictions/latest/
        """
        # Get the latest prediction per student
        latest_prediction_ids = Prediction.objects.values('student').annotate(
            latest_id=Max('id')
        ).values('latest_id')

        latest_predictions = self.get_queryset().filter(
            id__in=Subquery(latest_prediction_ids)
        ).order_by('-risk_score')

        serializer = self.get_serializer(latest_predictions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate ML predictions for students.

        POST /predictions/generate/
        Body: {"student_ids": [...]} or empty for all active students
        """
        from apps.students.models import Student
        from apps.grades.models import Grade
        from apps.attendance.models import Attendance

        student_ids = request.data.get('student_ids', [])

        # Get students
        if student_ids:
            students = Student.objects.filter(id__in=student_ids, status='active')
        else:
            students = Student.objects.filter(status='active')

        if not students.exists():
            return Response(
                {'error': 'Aucun étudiant actif trouvé.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Initialize predictor
        predictor = DropoutRiskPredictor()

        # Try to load active model
        active_model = MLModel.objects.filter(status=MLModel.Status.ACTIVE).first()
        model_loaded = False
        if active_model:
            try:
                predictor.load_model()
                model_loaded = True
            except FileNotFoundError:
                pass  # Will use heuristics

        predictions_created = []

        for student in students:
            # Gather student features
            features = self._gather_student_features(student)

            # Get prediction
            result = predictor.predict_risk(features)

            # Create prediction record
            risk_level_map = {
                'low': Prediction.RiskLevel.LOW,
                'medium': Prediction.RiskLevel.MEDIUM,
                'high': Prediction.RiskLevel.HIGH,
                'critical': Prediction.RiskLevel.CRITICAL,
            }

            prediction = Prediction.objects.create(
                student=student,
                risk_score=float(result['risk_score']),
                risk_level=risk_level_map.get(result['risk_level'], Prediction.RiskLevel.MEDIUM),
                predicted_success_rate=100 - float(result['risk_score']),
                factors=result.get('factors', []),
                model_version=active_model if model_loaded else None
            )

            # Update student risk fields
            student.risk_score = float(result['risk_score'])
            student.risk_level = result['risk_level']
            student.save(update_fields=['risk_score', 'risk_level', 'updated_at'])

            predictions_created.append({
                'student_id': str(student.id),
                'student_name': f"{student.first_name} {student.last_name}",
                'prediction_id': str(prediction.id),
                'risk_score': float(result['risk_score']),
                'risk_level': result['risk_level']
            })

        # Sort by risk score descending
        predictions_created.sort(key=lambda x: x['risk_score'], reverse=True)

        return Response({
            'success': True,
            'model_used': active_model.name if model_loaded else 'heuristics',
            'total_predictions': len(predictions_created),
            'predictions': predictions_created
        })

    def _gather_student_features(self, student):
        """Gather features for a student from database using the centralized function."""
        return calculate_student_features_from_db(student)

