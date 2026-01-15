"""
Celery tasks for Prediction app.
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_predictions_task(self, ml_model_id=None, session_id=None):
    """
    Async task to generate predictions for all active students.
    Uses the actual ML prediction logic from DropoutRiskPredictor.
    """
    from apps.students.models import Student
    from apps.ml.models import MLModel
    from apps.sessions.models import Session
    from apps.ml.services import DropoutRiskPredictor, calculate_student_features_from_db
    from .models import Prediction

    try:
        # Get ML model - REQUIRED (no heuristics fallback)
        active_model = None
        if ml_model_id:
            active_model = MLModel.objects.get(id=ml_model_id)
            logger.info(f"Generating predictions using model {active_model.name}")
        else:
            # Try to get active model
            active_model = MLModel.objects.filter(status=MLModel.Status.ACTIVE).first()
            if active_model:
                logger.info(f"Using active model: {active_model.name}")

        # REQUIRE a model - no heuristics
        if not active_model:
            logger.error("No active ML model found. Cannot generate predictions without a trained model.")
            return {
                'status': 'error',
                'error': 'NO_ACTIVE_MODEL',
                'message': 'No active ML model. Train and activate a model first.',
                'predictions_created': 0
            }

        # Get students
        if session_id:
            session = Session.objects.get(id=session_id)
            students = session.get_active_students()
            logger.info(f"Generating predictions for session: {session.name}")
        else:
            students = Student.objects.filter(status=Student.Status.ACTIVE)
            logger.info("Generating predictions for all active students")

        if not students.exists():
            logger.warning("No active students found")
            return {
                'status': 'success',
                'predictions_created': 0,
                'message': 'No active students found'
            }

        # Initialize predictor and load model
        predictor = DropoutRiskPredictor()

        try:
            predictor.load_model()
            logger.info("ML model loaded successfully")
        except FileNotFoundError:
            logger.error(f"Model file not found for {active_model.name}")
            return {
                'status': 'error',
                'error': 'MODEL_FILE_NOT_FOUND',
                'message': f'Model file for {active_model.name} not found. Retrain the model.',
                'predictions_created': 0
            }

        predictions_created = 0
        predictions_skipped = 0
        alerts_created = 0

        for student in students:
            try:
                # Gather student features
                features = calculate_student_features_from_db(student)

                # Get prediction
                result = predictor.predict_risk(features)

                # Skip if prediction failed (insufficient data)
                if result.get('error'):
                    predictions_skipped += 1
                    logger.warning(f"Skipped student {student.id}: {result.get('error_message')}")
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
                    risk_score=int(result['risk_score']),
                    risk_level=risk_level_map.get(result['risk_level'], Prediction.RiskLevel.MEDIUM),
                    predicted_success_rate=int(100 - result['risk_score']),
                    factors=result.get('factors', []),
                    model_version=active_model
                )

                # Update student risk fields
                student.risk_score = int(result['risk_score'])
                student.risk_level = result['risk_level']
                student.save(update_fields=['risk_score', 'risk_level', 'updated_at'])

                # Create alert automatically if risk is high or critical
                if prediction.risk_level in [Prediction.RiskLevel.HIGH, Prediction.RiskLevel.CRITICAL]:
                    from apps.alerts.models import Alert
                    
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

                predictions_created += 1

            except Exception as e:
                logger.error(f"Failed to generate prediction for student {student.id}: {str(e)}", exc_info=True)
                continue

        logger.info(f"Generated {predictions_created} predictions, skipped {predictions_skipped}, created {alerts_created} alerts")

        return {
            'status': 'success',
            'predictions_created': predictions_created,
            'predictions_skipped': predictions_skipped,
            'alerts_created': alerts_created,
            'model_used': f"{active_model.name} v{active_model.version}"
        }

    except MLModel.DoesNotExist:
        logger.error(f"ML Model {ml_model_id} not found")
        raise

    except Session.DoesNotExist:
        logger.error(f"Session {session_id} not found")
        raise

    except Exception as e:
        logger.error(f"Failed to generate predictions: {str(e)}", exc_info=True)
        raise


@shared_task(bind=True)
def generate_interventions_task(self, prediction_id):
    """
    Async task to generate recommended interventions for a prediction.
    """
    from .models import Prediction, RecommendedIntervention

    try:
        prediction = Prediction.objects.get(id=prediction_id)
        logger.info(f"Generating interventions for prediction {prediction.id}")

        # Clear existing interventions
        prediction.recommended_interventions.all().delete()

        # Generate interventions based on risk factors
        interventions = []

        # Attendance-based interventions
        if prediction.attendance_factor and prediction.attendance_factor > 40:
            interventions.append(
                RecommendedIntervention(
                    prediction=prediction,
                    intervention_type=RecommendedIntervention.InterventionType.ENGAGEMENT,
                    priority=RecommendedIntervention.Priority.HIGH,
                    title="Améliorer la présence en classe",
                    description="Contacter l'étudiant pour discuter des problèmes de présence.",
                    estimated_impact=25.0
                )
            )

        # Grade-based interventions
        if prediction.grade_factor and prediction.grade_factor > 40:
            interventions.append(
                RecommendedIntervention(
                    prediction=prediction,
                    intervention_type=RecommendedIntervention.InterventionType.TUTORING,
                    priority=RecommendedIntervention.Priority.HIGH,
                    title="Soutien académique",
                    description="Offrir du tutorat dans les cours où l'étudiant a des difficultés.",
                    estimated_impact=30.0
                )
            )

        # Critical risk interventions
        if prediction.risk_level == Prediction.RiskLevel.CRITICAL:
            interventions.append(
                RecommendedIntervention(
                    prediction=prediction,
                    intervention_type=RecommendedIntervention.InterventionType.COUNSELING,
                    priority=RecommendedIntervention.Priority.URGENT,
                    title="Rencontre avec conseiller",
                    description="Planifier une rencontre urgente avec un conseiller académique.",
                    estimated_impact=40.0
                )
            )

        # Bulk create interventions
        RecommendedIntervention.objects.bulk_create(interventions)

        logger.info(f"Generated {len(interventions)} interventions for prediction {prediction.id}")

        return {
            'status': 'success',
            'interventions_created': len(interventions)
        }

    except Prediction.DoesNotExist:
        logger.error(f"Prediction {prediction_id} not found")
        raise

    except Exception as e:
        logger.error(f"Failed to generate interventions: {str(e)}", exc_info=True)
        raise
