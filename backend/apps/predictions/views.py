"""
Views for Prediction app.

Permissions par rôle:
- ADMIN: Full access including generate
- DS: Full access including generate
- PEDAGOGICAL: Read-only access, can view predictions
- TEACHER: Read-only access to their students' predictions
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
from apps.core.mixins import RoleBasedPermissionMixin, AuditLogMixin
from apps.core.permissions import (
    IsAdmin, IsDSOrAdmin, CanViewPredictions, CanRunMLPredictions, IsPedagogicalOrAbove
)


class PredictionViewSet(RoleBasedPermissionMixin, AuditLogMixin, viewsets.ModelViewSet):
    """
    ViewSet for Prediction model.

    Provides CRUD operations and custom actions:
    - GET /predictions/ - List all predictions (filtered by role)
    - POST /predictions/ - Create a prediction (DS/Admin only)
    - GET /predictions/{id}/ - Retrieve a prediction
    - PUT/PATCH /predictions/{id}/ - Update a prediction (DS/Admin only)
    - DELETE /predictions/{id}/ - Delete a prediction (Admin only)
    - GET /predictions/student/{student_id}/ - Get predictions for a student
    - GET /predictions/statistics/ - Get prediction statistics
    - GET /predictions/at_risk/ - Get high-risk predictions (Pedagogical+)
    - POST /predictions/generate/ - Generate ML predictions (DS/Admin only)
    """
    queryset = Prediction.objects.all()
    permission_classes = [IsAuthenticated]

    # Role-based permissions per action
    permission_classes_by_action = {
        'list': [IsAuthenticated, CanViewPredictions],
        'retrieve': [IsAuthenticated, CanViewPredictions],
        'create': [IsAuthenticated, IsDSOrAdmin],
        'update': [IsAuthenticated, IsDSOrAdmin],
        'partial_update': [IsAuthenticated, IsDSOrAdmin],
        'destroy': [IsAuthenticated, IsAdmin],
        'generate': [IsAuthenticated, CanRunMLPredictions],
        'at_risk': [IsAuthenticated, IsPedagogicalOrAbove],
        'statistics': [IsAuthenticated, IsPedagogicalOrAbove],
        'latest': [IsAuthenticated, CanViewPredictions],
    }
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
        from apps.students.models import Student
        from django.shortcuts import get_object_or_404
        from rest_framework.exceptions import PermissionDenied

        student = get_object_or_404(Student, pk=student_id)

        # Verify the requesting user has access to this student's predictions
        if not request.user.has_elevated_permissions():
            if not request.user.is_teacher():
                raise PermissionDenied()
            # Teachers may only view predictions for their own students
            teacher_field = getattr(student, 'teacher', None)
            if teacher_field is not None and teacher_field != request.user:
                raise PermissionDenied()
            elif teacher_field is None and hasattr(student, 'enrollments'):
                teacher_classes = request.user.teaching_sessions.all()
                student_classes = student.enrollments.values_list('session_id', flat=True)
                if not teacher_classes.filter(id__in=student_classes).exists():
                    raise PermissionDenied()

        predictions = Prediction.objects.filter(
            student=student
        ).select_related('model_version').order_by('-created_at')

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

        # Try to load active model - REQUIRED (no heuristics fallback)
        active_model = MLModel.objects.filter(status=MLModel.Status.ACTIVE).first()

        if not active_model:
            return Response(
                {
                    'error': 'NO_ACTIVE_MODEL',
                    'message': 'Aucun modèle ML actif. Veuillez d\'abord entraîner et activer un modèle.',
                    'hint': 'Utilisez: python manage.py train_from_database && python manage.py activate_model --version <version>'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            predictor.load_model()
        except FileNotFoundError:
            return Response(
                {
                    'error': 'MODEL_FILE_NOT_FOUND',
                    'message': f'Fichier du modèle non trouvé pour la version {active_model.version}.',
                    'hint': 'Le modèle doit être ré-entraîné.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        predictions_created = []
        predictions_skipped = []
        alerts_created_count = 0

        for student in students:
            try:
                # Gather student features using centralized function
                features = calculate_student_features_from_db(student)

                # Get prediction (will return error if insufficient data)
                result = predictor.predict_risk(features)

                # Check if prediction failed due to insufficient data
                if result.get('error'):
                    predictions_skipped.append({
                        'student_id': str(student.id),
                        'student_name': f"{student.first_name} {student.last_name}",
                        'error': result['error'],
                        'message': result.get('error_message', ''),
                        'missing_features': result.get('missing_features', [])
                    })
                    continue

                # Create prediction record
                risk_level_map = {
                    'low': Prediction.RiskLevel.LOW,
                    'medium': Prediction.RiskLevel.MEDIUM,
                    'high': Prediction.RiskLevel.HIGH,
                    'critical': Prediction.RiskLevel.CRITICAL,
                }

                # Ensure risk_score is within valid range (0-100)
                risk_score = max(0, min(100, float(result['risk_score'])))

                prediction = Prediction.objects.create(
                    student=student,
                    risk_score=int(risk_score),
                    risk_level=risk_level_map.get(result['risk_level'], Prediction.RiskLevel.MEDIUM),
                    predicted_success_rate=int(100 - risk_score),
                    factors=result.get('factors', []),
                    model_version=active_model  # Always set - model is required now
                )

                # Update student risk fields
                student.risk_score = risk_score
                student.risk_level = result['risk_level']
                student.save(update_fields=['risk_score', 'risk_level', 'updated_at'])

                # Create alert automatically if risk is high or critical
                if prediction.risk_level in [Prediction.RiskLevel.HIGH, Prediction.RiskLevel.CRITICAL]:
                    from apps.alerts.models import Alert
                    
                    # Get top factors for the alert message
                    top_factors = prediction.get_top_factors(limit=3)
                    factors_list = []
                    for f in top_factors:
                        factor_name = f.get('name', 'N/A')
                        impact = f.get('impact', 0)
                        # Format impact as percentage
                        if isinstance(impact, (int, float)):
                            factors_list.append(f"{factor_name} ({impact:.1f}%)")
                        else:
                            factors_list.append(factor_name)
                    factors_text = ', '.join(factors_list) if factors_list else 'Non disponibles'
                    
                    # Determine alert level
                    alert_level = 'critical' if prediction.risk_level == Prediction.RiskLevel.CRITICAL else 'high'
                    
                    # Check if alert already exists
                    existing_alert = Alert.objects.filter(
                        student=student,
                        type=Alert.AlertType.PREDICTION,
                        status__in=[Alert.Status.NEW, Alert.Status.ACKNOWLEDGED]
                    ).exists()
                    
                    if not existing_alert:
                        # Create the alert using create_prediction_alert for prediction type
                        Alert.create_prediction_alert(
                            student=student,
                            message=f"L'étudiant {student.get_full_name()} présente un risque de décrochage {prediction.risk_level} (Score: {prediction.risk_score}%). Facteurs principaux: {factors_text}.",
                            level=alert_level
                        )
                        alerts_created_count += 1

                predictions_created.append({
                    'student_id': str(student.id),
                    'student_name': f"{student.first_name} {student.last_name}",
                    'prediction_id': str(prediction.id),
                    'risk_score': float(result['risk_score']),
                    'risk_level': result['risk_level']
                })
            except Exception as e:
                # Log error but continue with other students
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erreur lors de la génération de prédiction pour étudiant {student.id}: {e}", exc_info=True)
                continue

        # Sort by risk score descending
        predictions_created.sort(key=lambda x: x['risk_score'], reverse=True)

        return Response({
            'success': True,
            'model_used': f"{active_model.name} v{active_model.version}",
            'model_accuracy': float(active_model.accuracy) if active_model.accuracy else None,
            'total_predictions': len(predictions_created),
            'predictions_skipped': len(predictions_skipped),
            'skipped_details': predictions_skipped[:10],  # First 10 skipped for debugging
            'alerts_created': alerts_created_count,
            'predictions': predictions_created
        })

    def _gather_student_features(self, student):
        """Gather features for a student from database using the centralized function."""
        return calculate_student_features_from_db(student)

