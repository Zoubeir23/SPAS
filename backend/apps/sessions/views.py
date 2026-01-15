"""
Views for Sessions app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Session
from .serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Session model.

    Provides CRUD operations and custom actions:
    - GET /sessions/ - List all sessions
    - POST /sessions/ - Create a session
    - GET /sessions/{id}/ - Retrieve a session
    - PUT/PATCH /sessions/{id}/ - Update a session
    - DELETE /sessions/{id}/ - Delete a session
    - GET /sessions/{id}/students/ - Get all students in session
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'year']
    search_fields = ['name', 'year']
    ordering_fields = ['year', 'start_date', 'created_at']
    ordering = ['-year', '-start_date']

    def get_queryset(self):
        """Optimize queryset with prefetch_related."""
        queryset = Session.objects.prefetch_related('students')
        return queryset

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        Get all students in a session.

        GET /sessions/{id}/students/
        """
        session = self.get_object()

        # Import here to avoid circular imports
        from apps.students.models import Student
        from apps.students.serializers import StudentListSerializer

        students = Student.objects.filter(
            session=session
        ).select_related('program').order_by('last_name', 'first_name')

        serializer = StudentListSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Close a session (mark as completed).

        POST /sessions/{id}/close/
        """
        session = self.get_object()

        if session.status == Session.Status.COMPLETED:
            return Response(
                {'error': 'Cette session est déjà clôturée.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.status = Session.Status.COMPLETED
        session.save(update_fields=['status', 'updated_at'])

        return Response({
            'success': True,
            'message': 'Session clôturée avec succès.',
            'data': SessionSerializer(session).data
        })

    @action(detail=True, methods=['post'])
    def generate_predictions(self, request, pk=None):
        """
        Generate predictions for all active students in this session.

        POST /sessions/{id}/generate-predictions/
        """
        session = self.get_object()

        # Get all active students in this session
        students = session.get_active_students()

        if not students.exists():
            return Response(
                {'error': 'Aucun étudiant actif trouvé dans cette session.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Import here to avoid circular imports
        from apps.ml.services import DropoutRiskPredictor, calculate_student_features_from_db
        from apps.ml.models import MLModel
        from apps.predictions.models import Prediction
        from apps.alerts.models import Alert

        # Get student IDs
        student_ids = list(students.values_list('id', flat=True))

        # REQUIRE an active model - no heuristics fallback
        active_model = MLModel.objects.filter(status=MLModel.Status.ACTIVE).first()
        if not active_model:
            return Response(
                {
                    'error': 'NO_ACTIVE_MODEL',
                    'message': 'Aucun modèle ML actif. Veuillez d\'abord entraîner et activer un modèle.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize predictor and load model
        predictor = DropoutRiskPredictor()
        try:
            predictor.load_model()
        except FileNotFoundError:
            return Response(
                {
                    'error': 'MODEL_FILE_NOT_FOUND',
                    'message': f'Fichier du modèle non trouvé pour {active_model.name}. Ré-entraînez le modèle.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        predictions_created = []
        predictions_skipped = []
        alerts_created = 0

        for student in students:
            # Gather student features
            features = calculate_student_features_from_db(student)

            # Get prediction
            result = predictor.predict_risk(features)

            # Skip if prediction failed (insufficient data)
            if result.get('error'):
                predictions_skipped.append({
                    'student_id': str(student.id),
                    'student_name': f"{student.first_name} {student.last_name}",
                    'error': result.get('error_message')
                })
                continue

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
                model_version=active_model
            )

            # Update student risk fields
            student.risk_score = float(result['risk_score'])
            student.risk_level = result['risk_level']
            student.save(update_fields=['risk_score', 'risk_level', 'updated_at'])

            # Create alert automatically if risk is high or critical
            if prediction.risk_level in [Prediction.RiskLevel.HIGH, Prediction.RiskLevel.CRITICAL]:
                # Get top factors for the alert message
                top_factors = prediction.get_top_factors(limit=3)
                factors_text = ', '.join([
                    f"{f.get('name', 'N/A')} ({f.get('impact', 0):.1%})" 
                    for f in top_factors
                ]) if top_factors else 'Non disponibles'
                
                # Determine alert level
                alert_level = 'critical' if prediction.risk_level == Prediction.RiskLevel.CRITICAL else 'high'
                
                # Check if alert already exists
                existing_alert = Alert.objects.filter(
                    student=student,
                    type=Alert.AlertType.RISK,
                    status__in=[Alert.Status.NEW, Alert.Status.ACKNOWLEDGED]
                ).exists()

                if not existing_alert:
                    Alert.create_risk_alert(
                        student=student,
                        message=f"Score de risque: {prediction.risk_score}%. "
                               f"Facteurs principaux: {factors_text}.",
                        level=alert_level
                    )
                    alerts_created += 1

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
            'message': f'Prédictions générées pour {len(predictions_created)} étudiants de la session {session.name}.',
            'session_id': str(session.id),
            'session_name': session.name,
            'model_used': f"{active_model.name} v{active_model.version}",
            'total_predictions': len(predictions_created),
            'predictions_skipped': len(predictions_skipped),
            'skipped_details': predictions_skipped[:5],
            'alerts_created': alerts_created,
            'predictions': predictions_created
        })
