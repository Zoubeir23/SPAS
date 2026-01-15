"""
Django management command to train ML model directly from database data.

This command collects features from all students in the database,
prepares training labels based on actual outcomes, and trains a real XGBoost model.

NO synthetic data. NO heuristics. Real data only.
"""
import os
import sys
import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from django.db.models import Count
import logging

logger = logging.getLogger(__name__)

# Configure UTF-8 encoding for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


class Command(BaseCommand):
    help = """
    Train ML model from REAL database data only.

    This command:
    1. Extracts 24 features from each student's grades, attendance, and history
    2. Uses actual student outcomes (dropout, graduated, active) as labels
    3. Trains XGBoost model with SMOTE for class balancing
    4. Saves model and creates MLModel record

    Requirements:
    - At least 50 students with sufficient data
    - At least 10 students per outcome class
    - Each student must have at least 5 computed features
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--algorithm',
            type=str,
            choices=['xgboost', 'random_forest', 'gradient_boosting'],
            default='xgboost',
            help='ML algorithm to use (default: xgboost)'
        )
        parser.add_argument(
            '--min-students',
            type=int,
            default=50,
            help='Minimum number of students required (default: 50)'
        )
        parser.add_argument(
            '--min-features',
            type=int,
            default=5,
            help='Minimum features per student (default: 5)'
        )
        parser.add_argument(
            '--test-size',
            type=float,
            default=0.2,
            help='Test set proportion (default: 0.2)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Analyze data without training'
        )

    def handle(self, *args, **options):
        algorithm = options['algorithm']
        min_students = options['min_students']
        min_features = options['min_features']
        test_size = options['test_size']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('\n=== ENTRAINEMENT ML DEPUIS BASE DE DONNEES ===\n'))

        # Import models
        from apps.students.models import Student
        from apps.ml.services import (
            calculate_student_features_from_db,
            get_feature_completeness,
            DropoutRiskPredictor
        )
        from apps.ml.models import MLModel, TrainingJob

        # Step 1: Collect all students with their features
        self.stdout.write('Etape 1: Collecte des donnees etudiants...')

        students = Student.objects.all()
        total_students = students.count()

        if total_students < min_students:
            self.stdout.write(self.style.ERROR(
                f'\nErreur: Seulement {total_students} etudiants dans la base. '
                f'Minimum requis: {min_students}'
            ))
            self.stdout.write('\nPour tester avec moins de donnees, utilisez:')
            self.stdout.write(f'  python manage.py train_from_database --min-students {total_students}')
            return

        # Step 2: Compute features for each student
        self.stdout.write(f'\nEtape 2: Calcul des features pour {total_students} etudiants...')

        valid_data = []
        invalid_students = []
        feature_stats = {
            'total_features': 24,
            'avg_available': 0,
            'students_with_enough_features': 0
        }

        for i, student in enumerate(students):
            if (i + 1) % 100 == 0 or i == total_students - 1:
                self.stdout.write(f'  Traitement: {i + 1}/{total_students}', ending='\r')

            # Compute features
            features = calculate_student_features_from_db(student)
            completeness = get_feature_completeness(features)

            # Check if student has enough data
            if completeness['available_features'] >= min_features:
                # Determine label based on student status
                # 0 = Low risk (graduated, active with good performance)
                # 1 = Medium risk (active but struggling)
                # 2 = High risk (dropout, inactive, failed)
                if student.status == 'dropout' or student.status == 'inactive':
                    label = 2  # High risk
                elif student.status == 'graduated':
                    label = 0  # Low risk
                else:  # active
                    # For active students, use their risk_score if available
                    if student.risk_score is not None:
                        if student.risk_score >= 70:
                            label = 2
                        elif student.risk_score >= 40:
                            label = 1
                        else:
                            label = 0
                    else:
                        # Use average_grade as proxy
                        avg_grade = features.get('average_grade')
                        if avg_grade is not None:
                            if avg_grade < 8:
                                label = 2
                            elif avg_grade < 12:
                                label = 1
                            else:
                                label = 0
                        else:
                            # Cannot determine label, skip
                            invalid_students.append({
                                'id': str(student.id),
                                'reason': 'Cannot determine label'
                            })
                            continue

                valid_data.append({
                    'student_id': str(student.id),
                    'features': features,
                    'label': label,
                    'available_features': completeness['available_features']
                })
                feature_stats['students_with_enough_features'] += 1
            else:
                invalid_students.append({
                    'id': str(student.id),
                    'reason': f'Only {completeness["available_features"]} features available'
                })

        self.stdout.write('')  # New line after progress

        # Step 3: Report data statistics
        self.stdout.write(f'\nEtape 3: Analyse des donnees...')
        self.stdout.write(f'  - Etudiants valides: {len(valid_data)}/{total_students}')
        self.stdout.write(f'  - Etudiants invalides: {len(invalid_students)}')

        if len(valid_data) < min_students:
            self.stdout.write(self.style.ERROR(
                f'\nErreur: Seulement {len(valid_data)} etudiants avec donnees suffisantes. '
                f'Minimum requis: {min_students}'
            ))
            if invalid_students[:5]:
                self.stdout.write('\nExemples d\'etudiants exclus:')
                for s in invalid_students[:5]:
                    self.stdout.write(f'  - {s["id"]}: {s["reason"]}')
            return

        # Label distribution
        labels = [d['label'] for d in valid_data]
        label_counts = {
            'Faible risque (0)': labels.count(0),
            'Risque moyen (1)': labels.count(1),
            'Risque eleve (2)': labels.count(2),
        }
        self.stdout.write(f'\n  Distribution des labels:')
        for name, count in label_counts.items():
            pct = count / len(labels) * 100
            self.stdout.write(f'    - {name}: {count} ({pct:.1f}%)')

        # Check minimum per class
        min_per_class = min(label_counts.values())
        if min_per_class < 10:
            self.stdout.write(self.style.WARNING(
                f'\n  Attention: La classe minoritaire n\'a que {min_per_class} echantillons.'
            ))
            self.stdout.write('  SMOTE sera utilise pour equilibrer les donnees.')

        if dry_run:
            self.stdout.write(self.style.SUCCESS('\n=== MODE DRY-RUN: Analyse terminee ==='))
            return

        # Step 4: Prepare feature matrix
        self.stdout.write(f'\nEtape 4: Preparation de la matrice de features...')

        # Get feature names (24 features)
        feature_names = DropoutRiskPredictor.DEFAULT_FEATURES

        # Build X matrix (replace None with 0)
        X = []
        y = []
        for data in valid_data:
            row = []
            for fname in feature_names:
                val = data['features'].get(fname)
                row.append(val if val is not None else 0.0)
            X.append(row)
            y.append(data['label'])

        X = np.array(X, dtype=np.float32)
        y = np.array(y)

        self.stdout.write(f'  - Matrice X: {X.shape}')
        self.stdout.write(f'  - Vecteur y: {y.shape}')

        # Step 5: Create training job
        self.stdout.write(f'\nEtape 5: Creation du job d\'entrainement...')

        job = TrainingJob.objects.create(
            name=f'Training from database ({timezone.now().strftime("%Y-%m-%d %H:%M")})',
            description=f'Entrainement {algorithm} sur {len(X)} etudiants reels',
            job_type=TrainingJob.JobType.TRAIN,
            algorithm=algorithm,
            status=TrainingJob.Status.RUNNING,
            started_at=timezone.now(),
            created_by=None
        )
        self.stdout.write(f'  Job ID: {job.id}')

        # Step 6: Train model
        self.stdout.write(f'\nEtape 6: Entrainement du modele {algorithm}...')

        try:
            predictor = DropoutRiskPredictor()

            # Progress callback
            def progress_callback(progress, step, message=None):
                job.update_progress(progress, step, logs=message or '')
                self.stdout.write(f'  [{progress}%] {step}')

            # Train with SMOTE if imbalanced
            use_smote = min_per_class < len(X) * 0.25

            metrics = predictor.train(
                X, y,
                algorithm=algorithm,
                feature_names=feature_names,
                use_smote=use_smote,
                test_size=test_size,
                progress_callback=progress_callback
            )

            # Step 7: Save model
            self.stdout.write(f'\nEtape 7: Sauvegarde du modele...')
            model_path = predictor.save_model()
            self.stdout.write(f'  Fichier: {model_path}')

            # Determine version
            existing_versions = MLModel.objects.filter(
                name='DropoutRiskPredictor'
            ).values_list('version', flat=True)

            if existing_versions:
                max_v = max([int(v.split('.')[-1]) for v in existing_versions if v and '.' in v], default=0)
                new_version = f"1.0.{max_v + 1}"
            else:
                new_version = "1.0.0"

            # Convert metrics (0-1 to 0-100)
            def to_pct(val):
                v = float(val) if val else 0
                return min(100.0, max(0.0, v * 100 if v <= 1 else v))

            ml_model = MLModel.objects.create(
                name='DropoutRiskPredictor',
                version=new_version,
                model_type=algorithm,
                status=MLModel.Status.INACTIVE,
                accuracy=to_pct(metrics.get('accuracy', 0)),
                precision=to_pct(metrics.get('precision', 0)),
                recall=to_pct(metrics.get('recall', 0)),
                f1_score=to_pct(metrics.get('f1_score', 0)),
                trained_at=timezone.now(),
                training_data_size=len(X)
            )

            job.complete(ml_model)

            # Step 8: Summary
            self.stdout.write(self.style.SUCCESS('\n=== ENTRAINEMENT TERMINE AVEC SUCCES ==='))
            self.stdout.write(f'\nModele: {new_version}')
            self.stdout.write(f'Algorithme: {algorithm}')
            self.stdout.write(f'Donnees: {len(X)} etudiants reels')
            self.stdout.write(f'\nMetriques:')
            self.stdout.write(f'  - Accuracy:  {to_pct(metrics.get("accuracy", 0)):.2f}%')
            self.stdout.write(f'  - Precision: {to_pct(metrics.get("precision", 0)):.2f}%')
            self.stdout.write(f'  - Recall:    {to_pct(metrics.get("recall", 0)):.2f}%')
            self.stdout.write(f'  - F1-Score:  {to_pct(metrics.get("f1_score", 0)):.2f}%')

            self.stdout.write(f'\nPour ACTIVER ce modele:')
            self.stdout.write(f'  python manage.py activate_model --version {new_version}')

        except Exception as e:
            job.fail(str(e))
            self.stdout.write(self.style.ERROR(f'\nErreur: {e}'))
            logger.exception("Training failed")
            raise
