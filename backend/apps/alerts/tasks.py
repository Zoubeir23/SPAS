"""
Celery tasks for Alert app.
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def create_alerts_from_predictions(self):
    """
    Create alerts from recent predictions with high risk.
    """
    from apps.predictions.models import Prediction
    from .models import Alert

    try:
        # Get recent high-risk predictions without alerts
        high_risk_predictions = Prediction.objects.filter(
            is_at_risk=True,
            is_latest=True,
            alerts__isnull=True
        )

        alerts_created = 0

        for prediction in high_risk_predictions:
            # Determine severity based on risk level
            if prediction.risk_level == Prediction.RiskLevel.CRITICAL:
                severity = Alert.Severity.CRITICAL
            elif prediction.risk_level == Prediction.RiskLevel.HIGH:
                severity = Alert.Severity.WARNING
            else:
                severity = Alert.Severity.INFO

            # Create alert
            alert = Alert.objects.create(
                student=prediction.student,
                alert_type=Alert.AlertType.DROPOUT_RISK,
                severity=severity,
                title=f"Étudiant à risque: {prediction.student.get_full_name()}",
                message=f"Score de risque: {prediction.risk_score}%. "
                       f"Facteurs: Présence ({prediction.attendance_factor}%), "
                       f"Notes ({prediction.grade_factor}%), "
                       f"Engagement ({prediction.engagement_factor}%).",
                prediction=prediction
            )

            alerts_created += 1

        logger.info(f"Created {alerts_created} alerts from predictions")

        return {
            'status': 'success',
            'alerts_created': alerts_created
        }

    except Exception as e:
        logger.error(f"Failed to create alerts from predictions: {str(e)}", exc_info=True)
        raise


@shared_task(bind=True)
def check_low_attendance(self):
    """
    Create alerts for students with low attendance.
    """
    from apps.attendance.models import AttendanceSummary
    from apps.students.models import Student
    from .models import Alert

    try:
        # Get students with low attendance (< 70%)
        low_attendance = AttendanceSummary.objects.filter(
            attendance_rate__lt=70,
            enrollment__student__status=Student.Status.ACTIVE
        )

        alerts_created = 0

        for summary in low_attendance:
            # Check if alert already exists
            existing_alert = Alert.objects.filter(
                student=summary.enrollment.student,
                alert_type=Alert.AlertType.LOW_ATTENDANCE,
                status__in=[Alert.Status.ACTIVE, Alert.Status.ACKNOWLEDGED]
            ).exists()

            if not existing_alert:
                Alert.objects.create(
                    student=summary.enrollment.student,
                    alert_type=Alert.AlertType.LOW_ATTENDANCE,
                    severity=Alert.Severity.WARNING if summary.attendance_rate < 60 else Alert.Severity.INFO,
                    title=f"Faible présence: {summary.enrollment.student.get_full_name()}",
                    message=f"Taux de présence: {summary.attendance_rate}% "
                           f"dans {summary.enrollment.course_session.course.name}. "
                           f"Absences: {summary.absent_count}/{summary.total_classes}."
                )
                alerts_created += 1

        logger.info(f"Created {alerts_created} low attendance alerts")

        return {
            'status': 'success',
            'alerts_created': alerts_created
        }

    except Exception as e:
        logger.error(f"Failed to check low attendance: {str(e)}", exc_info=True)
        raise


@shared_task(bind=True)
def check_failing_grades(self):
    """
    Create alerts for students with failing grades.
    """
    from apps.grades.models import CourseGradeSummary
    from apps.students.models import Student
    from .models import Alert

    try:
        # Get students with failing grades
        failing_grades = CourseGradeSummary.objects.filter(
            is_passing=False,
            enrollment__student__status=Student.Status.ACTIVE
        )

        alerts_created = 0

        for summary in failing_grades:
            # Check if alert already exists
            existing_alert = Alert.objects.filter(
                student=summary.enrollment.student,
                alert_type=Alert.AlertType.FAILING_GRADES,
                status__in=[Alert.Status.ACTIVE, Alert.Status.ACKNOWLEDGED]
            ).exists()

            if not existing_alert:
                Alert.objects.create(
                    student=summary.enrollment.student,
                    alert_type=Alert.AlertType.FAILING_GRADES,
                    severity=Alert.Severity.WARNING,
                    title=f"Notes insuffisantes: {summary.enrollment.student.get_full_name()}",
                    message=f"Note finale: {summary.final_grade}% ({summary.letter_grade}) "
                           f"dans {summary.enrollment.course_session.course.name}."
                )
                alerts_created += 1

        logger.info(f"Created {alerts_created} failing grades alerts")

        return {
            'status': 'success',
            'alerts_created': alerts_created
        }

    except Exception as e:
        logger.error(f"Failed to check failing grades: {str(e)}", exc_info=True)
        raise
