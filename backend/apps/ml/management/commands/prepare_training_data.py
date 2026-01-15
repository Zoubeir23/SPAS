"""
Django management command to prepare training data from datasets for ML training.
This command extracts features and prepares data in the format expected by DropoutRiskPredictor.
"""
import os
import pandas as pd
import numpy as np
import joblib
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.ml.services import calculate_student_features_from_db
from apps.students.models import Student
from apps.grades.models import Grade
from apps.attendance.models import Attendance
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Prepare training data from database students for ML training'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='ml_models/training_data.csv',
            help='Output CSV file path'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'numpy', 'both'],
            default='both',
            help='Output format (default: both)'
        )

    def handle(self, *args, **options):
        output_path = options['output']
        output_format = options['format']

        self.stdout.write(self.style.SUCCESS('Preparation des donnees d\'entrainement\n'))

        # Get all students with sufficient data
        students = Student.objects.filter(status=Student.Status.ACTIVE)
        
        self.stdout.write(f'{students.count()} etudiants actifs trouves')

        # Prepare features and labels
        features_list = []
        labels_list = []
        student_ids = []

        for student in students:
            try:
                # Calculate features using the centralized function
                features = calculate_student_features_from_db(student)
                
                # Determine label based on student status and risk
                # 0 = low risk, 1 = medium risk, 2 = high risk
                if student.risk_level == 'low' or (student.risk_score or 0) < 25:
                    label = 0
                elif student.risk_level == 'medium' or (student.risk_score or 0) < 50:
                    label = 1
                else:
                    label = 2

                # Convert features dict to list (maintain order)
                feature_names = [
                    'average_grade', 'attendance_rate', 'assignments_completed',
                    'late_submissions', 'absences_count', 'consecutive_absences',
                    'grade_trend', 'participation_score', 'weeks_enrolled',
                    'failed_subjects'
                ]

                feature_values = [features.get(name, 0.0) for name in feature_names]
                
                features_list.append(feature_values)
                labels_list.append(label)
                student_ids.append(str(student.id))

            except Exception as e:
                logger.warning(f"Erreur pour étudiant {student.id}: {e}")
                continue

        if not features_list:
            self.stdout.write(self.style.ERROR('Aucune donnee preparee'))
            return

        # Convert to numpy arrays
        X = np.array(features_list)
        y = np.array(labels_list)

        self.stdout.write(self.style.SUCCESS(f'{len(features_list)} echantillons prepares'))
        self.stdout.write(f'   Features: {X.shape[1]}')
        self.stdout.write(f'   Labels distribution: {np.bincount(y)}')

        # Create output directory
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Save as CSV
        if output_format in ['csv', 'both']:
            df = pd.DataFrame(X, columns=feature_names)
            df['label'] = y
            df['student_id'] = student_ids
            df.to_csv(output_path, index=False)
            self.stdout.write(self.style.SUCCESS(f'Donnees sauvegardees en CSV: {output_path}'))

        # Save as numpy arrays
        if output_format in ['numpy', 'both']:
            np_path = output_path.replace('.csv', '_X.npy')
            np.save(np_path, X)
            self.stdout.write(self.style.SUCCESS(f'Features sauvegardees: {np_path}'))

            y_path = output_path.replace('.csv', '_y.npy')
            np.save(y_path, y)
            self.stdout.write(self.style.SUCCESS(f'Labels sauvegardes: {y_path}'))

        # Save feature names
        feature_names_path = output_path.replace('.csv', '_feature_names.pkl')
        joblib.dump(feature_names, feature_names_path)
        self.stdout.write(self.style.SUCCESS(f'Noms des features sauvegardes: {feature_names_path}'))

        self.stdout.write(self.style.SUCCESS('\nPreparation terminee!'))

