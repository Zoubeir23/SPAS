"""
Views for ML app.
"""
import logging
from django.db import models
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .models import MLModel, TrainingJob
from .serializers import (
    MLModelSerializer, MLModelListSerializer,
    TrainingJobSerializer, TrainingJobListSerializer, TrainingJobCreateSerializer,
    RiskPredictionRequestSerializer, BulkRiskPredictionRequestSerializer
)
from .services import DropoutRiskPredictor, calculate_student_features_from_db
from .tasks import run_training_job

logger = logging.getLogger(__name__)


class MLModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MLModel model.

    Provides CRUD operations and custom actions:
    - GET /models/ - List all ML models
    - POST /models/ - Create an ML model (admin only)
    - GET /models/{id}/ - Retrieve an ML model
    - PUT/PATCH /models/{id}/ - Update an ML model (admin only)
    - DELETE /models/{id}/ - Delete an ML model (admin only)
    - POST /models/{id}/activate/ - Activate a model
    - GET /models/active/ - Get the active model
    """
    queryset = MLModel.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'name']
    search_fields = ['name', 'version']
    ordering_fields = ['trained_at', 'accuracy', 'created_at']
    ordering = ['-trained_at']

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return MLModelListSerializer
        return MLModelSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()

        # Filter by status
        model_status = self.request.query_params.get('status', None)
        if model_status and model_status != 'all':
            queryset = queryset.filter(status=model_status)

        return queryset

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a model (deactivates other models with the same name).

        POST /models/{id}/activate/
        """
        model = self.get_object()
        model.activate()

        return Response({
            'success': True,
            'message': f'Modèle {model.name} v{model.version} activé.',
            'data': MLModelSerializer(model).data
        })

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archive a model (marks it as archived, does not delete it).

        POST /models/{id}/archive/
        """
        model = self.get_object()
        
        if model.status == MLModel.Status.ACTIVE:
            return Response(
                {'error': 'Impossible d\'archiver un modèle actif. Désactivez-le d\'abord.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if model.status == MLModel.Status.ARCHIVED:
            return Response(
                {'error': 'Ce modèle est déjà archivé.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        model.status = MLModel.Status.ARCHIVED
        model.save(update_fields=['status', 'updated_at'])

        return Response({
            'success': True,
            'message': f'Modèle {model.name} v{model.version} archivé avec succès.',
            'data': MLModelSerializer(model).data
        })

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get the currently active model.

        GET /models/active/
        """
        active_model = self.get_queryset().filter(status=MLModel.Status.ACTIVE).first()

        if active_model:
            serializer = MLModelSerializer(active_model)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Aucun modèle actif trouvé.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get ML model statistics.

        GET /models/statistics/
        """
        from django.db.models import Avg, Max

        queryset = self.get_queryset()

        stats = {
            'total_models': queryset.count(),
            'active_models': queryset.filter(status=MLModel.Status.ACTIVE).count(),
            'inactive_models': queryset.filter(status=MLModel.Status.INACTIVE).count(),
            'training_models': queryset.filter(status=MLModel.Status.TRAINING).count(),
            'archived_models': queryset.filter(status=MLModel.Status.ARCHIVED).count(),
        }

        # Get best model metrics
        best_metrics = queryset.aggregate(
            best_accuracy=Max('accuracy'),
            best_precision=Max('precision'),
            best_recall=Max('recall'),
            best_f1=Max('f1_score'),
            avg_accuracy=Avg('accuracy'),
        )

        return Response({
            'statistics': stats,
            'best_metrics': best_metrics
        })


class TrainingJobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TrainingJob model.

    Provides CRUD operations and custom actions:
    - GET /training-jobs/ - List all training jobs
    - POST /training-jobs/ - Create and start a training job
    - GET /training-jobs/{id}/ - Retrieve a training job
    - DELETE /training-jobs/{id}/ - Cancel/delete a training job
    - POST /training-jobs/{id}/cancel/ - Cancel a running job
    - GET /training-jobs/{id}/logs/ - Get training logs
    """
    queryset = TrainingJob.objects.select_related('created_by', 'resulting_model').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'job_type', 'algorithm']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'started_at', 'completed_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return TrainingJobListSerializer
        if self.action == 'create':
            return TrainingJobCreateSerializer
        return TrainingJobSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'destroy', 'cancel']:
            return [IsAdminUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Create training job and start training in background."""
        job = serializer.save(created_by=self.request.user)

        # Start training in background task
        run_training_job.delay(job.id)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a running training job.

        POST /training-jobs/{id}/cancel/
        """
        job = self.get_object()

        if job.status not in [TrainingJob.Status.PENDING, TrainingJob.Status.RUNNING]:
            return Response(
                {'error': 'Seuls les jobs en attente ou en cours peuvent être annulés.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        job.status = TrainingJob.Status.CANCELLED
        job.save(update_fields=['status', 'updated_at'])

        return Response({
            'success': True,
            'message': f'Job {job.name} annulé.',
            'data': TrainingJobSerializer(job).data
        })

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """
        Get training job logs.

        GET /training-jobs/{id}/logs/
        """
        job = self.get_object()
        return Response({
            'id': str(job.id),
            'name': job.name,
            'status': job.status,
            'progress': job.progress,
            'current_step': job.current_step,
            'logs': job.logs
        })


class PredictionViewSet(viewsets.ViewSet):
    """
    ViewSet for ML predictions.

    Provides prediction endpoints:
    - POST /predictions/predict/ - Predict risk for a single student
    - POST /predictions/predict-bulk/ - Predict risk for multiple students
    - GET /predictions/model-info/ - Get active model information
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._predictor = None

    def get_predictor(self):
        """Get or initialize the predictor with active model."""
        if self._predictor is None:
            self._predictor = DropoutRiskPredictor()

            # Try to load active model
            active_model = MLModel.objects.filter(status=MLModel.Status.ACTIVE).first()
            if active_model:
                try:
                    self._predictor.load_model()
                except FileNotFoundError:
                    logger.warning("Active model file not found. Using heuristics.")
                    pass  # Use untrained predictor (will use heuristics)
                except Exception as e:
                    logger.error(f"Error loading model: {e}. Using heuristics.")
                    pass

        return self._predictor

    @action(detail=False, methods=['post'])
    def predict(self, request):
        """
        Predict dropout risk for a single student.

        POST /predictions/predict/
        Body: {"student_id": "uuid"}
        """
        from apps.students.models import Student
        from apps.grades.models import Grade
        from apps.attendance.models import Attendance

        serializer = RiskPredictionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student_id = serializer.validated_data['student_id']

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Étudiant non trouvé.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Gather student features
        features = self._gather_student_features(student)

        # Get prediction
        predictor = self.get_predictor()
        prediction = predictor.predict_risk(features)

        # Update student risk fields
        student.risk_score = prediction['risk_score']
        student.risk_level = prediction['risk_level']
        student.save(update_fields=['risk_score', 'risk_level', 'updated_at'])

        return Response({
            'student_id': str(student.id),
            'student_name': f"{student.first_name} {student.last_name}",
            'prediction': prediction
        })

    @action(detail=False, methods=['post'], url_path='predict-bulk')
    def predict_bulk(self, request):
        """
        Predict dropout risk for multiple students.

        POST /predictions/predict-bulk/
        Body: {"student_ids": [...], "program_id": "uuid", "risk_threshold": 50}
        """
        from apps.students.models import Student

        serializer = BulkRiskPredictionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student_ids = serializer.validated_data.get('student_ids', [])
        program_id = serializer.validated_data.get('program_id')
        risk_threshold = serializer.validated_data.get('risk_threshold', 0)

        # Build queryset
        queryset = Student.objects.filter(status='active')

        if student_ids:
            queryset = queryset.filter(id__in=student_ids)
        if program_id:
            queryset = queryset.filter(program_id=program_id)

        predictor = self.get_predictor()
        predictions = []

        for student in queryset:
            features = self._gather_student_features(student)
            prediction = predictor.predict_risk(features)

            if prediction['risk_score'] >= risk_threshold:
                # Update student
                student.risk_score = prediction['risk_score']
                student.risk_level = prediction['risk_level']
                student.save(update_fields=['risk_score', 'risk_level', 'updated_at'])

                predictions.append({
                    'student_id': str(student.id),
                    'student_name': f"{student.first_name} {student.last_name}",
                    'program': student.program.name if student.program else None,
                    'prediction': prediction
                })

        # Sort by risk score descending
        predictions.sort(key=lambda x: x['prediction']['risk_score'], reverse=True)

        return Response({
            'total_students': queryset.count(),
            'predictions_count': len(predictions),
            'risk_threshold': risk_threshold,
            'predictions': predictions
        })

    @action(detail=False, methods=['get'], url_path='model-info')
    def model_info(self, request):
        """
        Get information about the active prediction model.

        GET /predictions/model-info/
        """
        active_model = MLModel.objects.filter(status=MLModel.Status.ACTIVE).first()

        if active_model:
            return Response({
                'model_loaded': True,
                'model': MLModelSerializer(active_model).data,
                'features': DropoutRiskPredictor.DEFAULT_FEATURES
            })
        else:
            return Response({
                'model_loaded': False,
                'message': 'Aucun modèle actif. Les prédictions utilisent des heuristiques.',
                'features': DropoutRiskPredictor.DEFAULT_FEATURES
            })

    def _gather_student_features(self, student):
        """
        Gather features for a student from various sources.
        """
        # Use the service function to calculate real features from DB
        return calculate_student_features_from_db(student)
