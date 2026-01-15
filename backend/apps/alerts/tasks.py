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
    Create alerts from recent high-risk predictions that don't have alerts yet.
    """
    from apps.predictions.models import Prediction
    from .models import Alert
    from django.db.models import Max

    try:
        # Get the latest prediction for each student
        latest_prediction_ids = Prediction.objects.values('student').annotate(
            latest_id=Max('id')
        ).values_list('latest_id', flat=True)

        # Get high-risk predictions (HIGH or CRITICAL) that are the latest for each student
        high_risk_predictions = Prediction.objects.filter(
            id__in=latest_prediction_ids,
            risk_level__in=[Prediction.RiskLevel.HIGH, Prediction.RiskLevel.CRITICAL]
        ).select_related('student')

        alerts_created = 0

        for prediction in high_risk_predictions:
            # Check if an alert already exists for this prediction/student
            existing_alert = Alert.objects.filter(
                student=prediction.student,
                type=Alert.AlertType.RISK,
                status__in=[Alert.Status.NEW, Alert.Status.ACKNOWLEDGED]
            ).exists()

            if not existing_alert:
                # Get top factors for the alert message
                top_factors = prediction.get_top_factors(limit=3)
                factors_text = ', '.join([
                    f"{f.get('name', 'N/A')} ({f.get('impact', 0):.1%})" 
                    for f in top_factors
                ]) if top_factors else 'Non disponibles'

                # Determine alert level based on risk level
                alert_level = 'critical' if prediction.risk_level == Prediction.RiskLevel.CRITICAL else 'high'

                # Create the alert
                Alert.create_risk_alert(
                    student=prediction.student,
                    message=f"Score de risque: {prediction.risk_score}%. "
                           f"Facteurs principaux: {factors_text}.",
                    level=alert_level
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
    Create alerts for students with low attendance (< 70%).
    """
    from apps.attendance.models import Attendance
    from apps.students.models import Student
    from .models import Alert
    from django.db.models import Count, Q

    try:
        # Get all active students
        students = Student.objects.filter(status=Student.Status.ACTIVE)

        alerts_created = 0
        threshold = 70  # 70% attendance threshold

        for student in students:
            # Get attendance records for this student
            attendance_records = Attendance.objects.filter(student=student)
            total = attendance_records.count()

            if total > 0:
                # Calculate attendance rate
                present_count = attendance_records.filter(status=Attendance.Status.PRESENT).count()
                attendance_rate = (present_count / total) * 100

                # Check if attendance is below threshold
                if attendance_rate < threshold:
                    # Check if alert already exists
                    existing_alert = Alert.objects.filter(
                        student=student,
                        type=Alert.AlertType.ATTENDANCE,
                        status__in=[Alert.Status.NEW, Alert.Status.ACKNOWLEDGED]
                    ).exists()

                    if not existing_alert:
                        # Determine alert level
                        alert_level = 'high' if attendance_rate < 60 else 'medium'

                        Alert.create_attendance_alert(
                            student=student,
                            message=f"Taux de présence faible: {attendance_rate:.1f}%. "
                                   f"Présent: {present_count}/{total} cours.",
                            level=alert_level
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
    Create alerts for students with failing grades (< 10/20 or < 50%).
    """
    from apps.grades.models import Grade
    from apps.students.models import Student
    from .models import Alert
    from django.db.models import Avg

    try:
        # Get all active students
        students = Student.objects.filter(status=Student.Status.ACTIVE)

        alerts_created = 0
        passing_threshold = 10.0  # 10/20 or 50%

        for student in students:
            # Get all grades for this student
            grades = Grade.objects.filter(student=student)
            
            if grades.exists():
                # Calculate average grade
                avg_grade = grades.aggregate(avg=Avg('score'))['avg'] or 0

                # Check if average is below passing threshold
                if avg_grade < passing_threshold:
                    # Check if alert already exists
                    existing_alert = Alert.objects.filter(
                        student=student,
                        type=Alert.AlertType.PERFORMANCE,
                        status__in=[Alert.Status.NEW, Alert.Status.ACKNOWLEDGED]
                    ).exists()

                    if not existing_alert:
                        Alert.create_performance_alert(
                            student=student,
                            message=f"Moyenne générale faible: {avg_grade:.1f}/20. "
                                   f"Nombre de notes: {grades.count()}.",
                            level='high'
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
