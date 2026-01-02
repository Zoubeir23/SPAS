#!/usr/bin/env python
"""Test generate predictions directly."""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from apps.predictions.views import PredictionViewSet
from apps.students.models import Student
from apps.ml.models import MLModel
from apps.ml.services import DropoutRiskPredictor


def test_generate():
    print("=" * 60)
    print("Testing prediction generation")
    print("=" * 60)
    
    # 1. Check active model
    active_model = MLModel.objects.filter(status='active').first()
    print(f"\n1. Active model: {active_model}")
    
    # 2. Try to load model
    print("\n2. Loading model...")
    predictor = DropoutRiskPredictor()
    try:
        predictor.load_model()
        print(f"   Model loaded: version {predictor.model_version}")
        model_loaded = True
    except Exception as e:
        print(f"   Error loading model: {e}")
        model_loaded = False
    
    # 3. Get students
    students = Student.objects.filter(status='active')
    print(f"\n3. Found {students.count()} active students")
    
    # 4. Test prediction for one student
    if students.exists() and model_loaded:
        student = students.first()
        print(f"\n4. Testing prediction for: {student.first_name} {student.last_name}")
        
        # Gather features
        from django.db.models import Avg, Count, Q
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
        
        print(f"   Features: {features}")
        
        # Get prediction
        try:
            result = predictor.predict_risk(features)
            print(f"\n   Prediction result:")
            print(f"     Risk score: {result['risk_score']}")
            print(f"     Risk level: {result['risk_level']}")
            print(f"     Model version: {result.get('model_version', 'N/A')}")
        except Exception as e:
            import traceback
            print(f"\n   Error predicting: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    test_generate()
