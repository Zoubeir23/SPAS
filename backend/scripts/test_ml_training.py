#!/usr/bin/env python
"""
Test ML training workflow end-to-end.
"""
import os
import sys
import time
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from apps.ml.models import MLModel, TrainingJob
from apps.ml.services import DropoutRiskPredictor, generate_synthetic_training_data
from apps.users.models import User
from apps.students.models import Student
from apps.predictions.models import Prediction
from django.utils import timezone


def test_ml_training_workflow():
    """Test the complete ML training workflow."""
    
    print("=" * 60)
    print("TEST ML TRAINING WORKFLOW")
    print("=" * 60)
    
    # 1. Get admin user
    admin = User.objects.filter(role='admin').first()
    if not admin:
        print("ERROR: No admin user found!")
        return False
    print(f"\n1. Admin user: {admin.email}")
    
    # 2. Create a training job
    print("\n2. Creating training job...")
    job = TrainingJob.objects.create(
        name="Test ML Training",
        description="Training a Random Forest model for dropout prediction",
        job_type='train',
        algorithm='random_forest',
        created_by=admin
    )
    print(f"   Job created: {job.id} - Status: {job.status}")
    
    # 3. Start training
    print("\n3. Starting training...")
    job.start()
    print(f"   Job started at: {job.started_at}")
    
    # 4. Initialize predictor and generate data
    print("\n4. Generating synthetic training data...")
    predictor = DropoutRiskPredictor()
    X, y = generate_synthetic_training_data(n_samples=500)
    print(f"   Data: {X.shape[0]} samples, {X.shape[1]} features")
    
    # 5. Train the model
    print("\n5. Training model...")
    
    def progress_callback(progress, step, details=''):
        job.update_progress(progress, step)
        if progress % 20 == 0:
            print(f"   Progress: {progress}% - {step}")
    
    metrics = predictor.train(X, y, progress_callback=progress_callback)
    print(f"\n   Training complete!")
    print(f"   Accuracy:  {metrics['accuracy']:.1f}%")
    print(f"   Precision: {metrics['precision']:.1f}%")
    print(f"   Recall:    {metrics['recall']:.1f}%")
    print(f"   F1 Score:  {metrics['f1_score']:.1f}%")
    
    # 6. Save the model
    print("\n6. Saving model...")
    model_path = predictor.save_model()
    print(f"   Model saved to: {model_path}")
    
    # 7. Create MLModel record
    print("\n7. Creating MLModel record...")
    existing_count = MLModel.objects.filter(name='DropoutRiskPredictor').count()
    new_version = f"1.0.{existing_count}"
    
    # Metrics are already percentages (0-100), use them directly
    ml_model = MLModel.objects.create(
        name='DropoutRiskPredictor',
        version=new_version,
        status=MLModel.Status.INACTIVE,
        accuracy=metrics['accuracy'],  # Already 0-100
        precision=metrics['precision'],  # Already 0-100
        recall=metrics['recall'],  # Already 0-100
        f1_score=metrics['f1_score'],  # Already 0-100
        trained_at=timezone.now(),
        training_data_size=500
    )
    print(f"   MLModel created: {ml_model.name} v{ml_model.version}")
    
    # 8. Complete the training job
    job.complete(ml_model)
    print(f"\n8. Training job completed!")
    print(f"   Job status: {job.status}")
    print(f"   Resulting model: {job.resulting_model}")
    
    # 9. Activate the model
    print("\n9. Activating model...")
    ml_model.activate()
    print(f"   Model status: {ml_model.status}")
    
    # 10. Test predictions with the trained model
    print("\n10. Testing predictions with trained model...")
    
    # Load the model
    new_predictor = DropoutRiskPredictor()
    new_predictor.load_model(model_path)
    print(f"    Model loaded successfully!")
    
    # Test predictions for existing students
    students = Student.objects.filter(status='active')[:3]
    
    for student in students:
        features = {
            'average_grade': 12,
            'attendance_rate': 85,
            'assignments_completed': 90,
            'late_submissions': 2,
            'absences_count': 3,
            'consecutive_absences': 1,
            'grade_trend': 0.1,
            'participation_score': 75,
            'weeks_enrolled': 16,
            'failed_subjects': 0
        }
        
        result = new_predictor.predict_risk(features)
        print(f"\n    {student.first_name} {student.last_name}:")
        print(f"      Risk Score: {result['risk_score']}")
        print(f"      Risk Level: {result['risk_level']}")
        print(f"      Confidence: {result['confidence']}")
        print(f"      Model Version: {result['model_version']}")
    
    print("\n" + "=" * 60)
    print("ML TRAINING WORKFLOW TEST COMPLETE!")
    print("=" * 60)
    
    # Summary
    print("\nSummary:")
    print(f"  - Training Jobs: {TrainingJob.objects.count()}")
    print(f"  - ML Models: {MLModel.objects.count()}")
    print(f"  - Active Model: {MLModel.objects.filter(status='active').first()}")
    print(f"  - Predictions: {Prediction.objects.count()}")
    
    return True


if __name__ == '__main__':
    success = test_ml_training_workflow()
    sys.exit(0 if success else 1)
