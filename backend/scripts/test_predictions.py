#!/usr/bin/env python
"""Test prediction generation."""
import os
import sys
import django
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from apps.students.models import Student
from apps.ml.services import DropoutRiskPredictor
from apps.predictions.models import Prediction
from apps.ml.models import MLModel
from apps.grades.models import Grade
from apps.attendance.models import Attendance
from django.db.models import Avg, Count, Q


def test_predictions():
    students = Student.objects.filter(status='active')
    print(f'Found {students.count()} students')

    predictor = DropoutRiskPredictor()
    active_model = MLModel.objects.filter(status=MLModel.Status.ACTIVE).first()
    print(f'Active model: {active_model}')

    for student in students:
        print(f'\nProcessing {student.first_name} {student.last_name}...')
        try:
            features = {}
            grade_stats = Grade.objects.filter(student=student).aggregate(
                avg_grade=Avg('value'),
                total_grades=Count('id')
            )
            features['average_grade'] = float(grade_stats['avg_grade'] or 10)
            
            attendance_stats = Attendance.objects.filter(student=student).aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(status='present')),
                absent=Count('id', filter=Q(status='absent'))
            )
            total = attendance_stats['total'] or 1
            features['attendance_rate'] = (attendance_stats['present'] or 0) / total * 100
            features['absences_count'] = attendance_stats['absent'] or 0
            
            print(f'  Features: {features}')
            
            result = predictor.predict_risk(features)
            print(f'  Score: {result["risk_score"]}, Level: {result["risk_level"]}')
            
            # Create prediction
            risk_level_map = {
                'low': Prediction.RiskLevel.LOW,
                'medium': Prediction.RiskLevel.MEDIUM,
                'high': Prediction.RiskLevel.HIGH,
                'critical': Prediction.RiskLevel.CRITICAL,
            }
            
            prediction = Prediction.objects.create(
                student=student,
                risk_score=result['risk_score'],
                risk_level=risk_level_map.get(result['risk_level'], Prediction.RiskLevel.MEDIUM),
                predicted_success_rate=100 - result['risk_score'],
                factors=result.get('factors', []),
                model_version=active_model
            )
            print(f'  Prediction created: {prediction.id}')
            
        except Exception as e:
            print(f'  Error: {e}')
            traceback.print_exc()
            return False
    
    return True


if __name__ == '__main__':
    success = test_predictions()
    print(f'\n{"Success!" if success else "Failed!"}')
