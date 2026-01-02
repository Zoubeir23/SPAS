#!/usr/bin/env python
"""Debug the generate endpoint."""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

import traceback
from apps.students.models import Student
from apps.predictions.models import Prediction
from apps.ml.models import MLModel
from apps.ml.services import DropoutRiskPredictor
from django.db.models import Avg, Count, Q


def gather_features(student):
    """Gather features for a student."""
    from apps.grades.models import Grade
    from apps.attendance.models import Attendance

    features = {}

    grade_stats = Grade.objects.filter(student=student).aggregate(
        avg_grade=Avg('value'),
        total_grades=Count('id')
    )
    features['average_grade'] = float(grade_stats['avg_grade'] or 10)

    attendance_stats = Attendance.objects.filter(student=student).aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late'))
    )

    total = attendance_stats['total'] or 1
    features['attendance_rate'] = (attendance_stats['present'] or 0) / total * 100
    features['absences_count'] = attendance_stats['absent'] or 0
    features['late_submissions'] = attendance_stats['late'] or 0
    features['assignments_completed'] = 80
    features['consecutive_absences'] = 0
    features['grade_trend'] = 0
    features['participation_score'] = 70
    features['weeks_enrolled'] = 16
    features['failed_subjects'] = 0

    return features


def test_full_generate():
    print("Testing full generate flow...")
    
    students = Student.objects.filter(status='active')
    print(f"Found {students.count()} students")

    predictor = DropoutRiskPredictor()
    active_model = MLModel.objects.filter(status=MLModel.Status.ACTIVE).first()
    print(f"Active model: {active_model}")
    
    model_loaded = False
    if active_model:
        try:
            predictor.load_model()
            model_loaded = True
            print("Model loaded successfully")
        except Exception as e:
            print(f"Failed to load model: {e}")
            traceback.print_exc()

    predictions_created = []

    for student in students:
        print(f"\nProcessing: {student.first_name} {student.last_name}")
        
        try:
            features = gather_features(student)
            print(f"  Features: {features}")
            
            result = predictor.predict_risk(features)
            print(f"  Result: score={result['risk_score']}, level={result['risk_level']}")

            risk_level_map = {
                'low': Prediction.RiskLevel.LOW,
                'medium': Prediction.RiskLevel.MEDIUM,
                'high': Prediction.RiskLevel.HIGH,
                'critical': Prediction.RiskLevel.CRITICAL,
            }

            print(f"  Creating prediction record...")
            prediction = Prediction.objects.create(
                student=student,
                risk_score=result['risk_score'],
                risk_level=risk_level_map.get(result['risk_level'], Prediction.RiskLevel.MEDIUM),
                predicted_success_rate=100 - result['risk_score'],
                factors=result.get('factors', []),
                model_version=active_model if model_loaded else None
            )
            print(f"  Prediction created: {prediction.id}")

            print(f"  Updating student...")
            student.risk_score = result['risk_score']
            student.risk_level = result['risk_level']
            student.save(update_fields=['risk_score', 'risk_level', 'updated_at'])
            print(f"  Student updated")

            predictions_created.append({
                'student_id': str(student.id),
                'student_name': f"{student.first_name} {student.last_name}",
                'prediction_id': str(prediction.id),
                'risk_score': result['risk_score'],
                'risk_level': result['risk_level']
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            traceback.print_exc()

    print(f"\n\nCreated {len(predictions_created)} predictions")
    for p in predictions_created:
        print(f"  {p['student_name']}: {p['risk_score']}")


if __name__ == '__main__':
    test_full_generate()
