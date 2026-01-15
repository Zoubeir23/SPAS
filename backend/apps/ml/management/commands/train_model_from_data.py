"""
Django management command to train ML model from prepared training data.
"""
import os
import sys
import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.ml.services import DropoutRiskPredictor, load_training_data_from_csv
from apps.ml.models import MLModel, TrainingJob
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


class Command(BaseCommand):
    help = 'Train ML model from prepared training data CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            type=str,
            default='ml_models/training_data.csv',
            help='Path to training data CSV file'
        )
        parser.add_argument(
            '--algorithm',
            type=str,
            choices=['xgboost', 'random_forest', 'gradient_boosting', 'logistic_regression'],
            default='xgboost',
            help='ML algorithm to use (default: xgboost)'
        )
        parser.add_argument(
            '--use-synthetic',
            action='store_true',
            help='Use synthetic data if real data is insufficient'
        )

    def handle(self, *args, **options):
        data_path = options['data']
        algorithm = options['algorithm']
        use_synthetic = options['use_synthetic']

        self.stdout.write(self.style.SUCCESS('Debut de l\'entrainement du modele ML\n'))

        # Check if data file exists
        if not os.path.exists(data_path):
            self.stdout.write(self.style.ERROR(f'Fichier de donnees non trouve: {data_path}'))
            if use_synthetic:
                self.stdout.write('Generation de donnees synthetiques...')
                from apps.ml.services import generate_synthetic_training_data
                X, y = generate_synthetic_training_data(n_samples=1000)
                feature_names = [
                    'average_grade', 'attendance_rate', 'assignments_completed',
                    'late_submissions', 'absences_count', 'consecutive_absences',
                    'grade_trend', 'participation_score', 'weeks_enrolled',
                    'failed_subjects'
                ]
            else:
                self.stdout.write('Utilisez --use-synthetic pour generer des donnees synthetiques')
                return
        else:
            # Load data from CSV
            try:
                X, y, feature_names = load_training_data_from_csv(data_path)
                self.stdout.write(f'Donnees chargees: {len(X)} echantillons, {len(feature_names)} features')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erreur lors du chargement: {e}'))
                return

        # Check data balance
        unique, counts = np.unique(y, return_counts=True)
        self.stdout.write(f'Distribution des labels: {dict(zip(unique, counts))}')

        if len(unique) < 2:
            self.stdout.write(self.style.WARNING('Attention: Donnees desequilibrees. Utilisation de SMOTE recommande.'))
        elif min(counts) < 10:
            self.stdout.write(self.style.WARNING('Attention: Certaines classes ont tres peu d\'echantillons.'))

        # Create training job
        job = TrainingJob.objects.create(
            name=f'Training from {os.path.basename(data_path)}',
            description=f'Entrainement avec {algorithm} sur {len(X)} echantillons',
            job_type=TrainingJob.JobType.TRAIN,
            algorithm=algorithm,
            status=TrainingJob.Status.RUNNING,
            started_at=timezone.now(),
            created_by=None  # System job
        )

        self.stdout.write(f'Job d\'entrainement cree: {job.id}')

        try:
            # Initialize predictor
            predictor = DropoutRiskPredictor()

            # Progress callback
            def progress_callback(progress, step, message=None):
                job.update_progress(progress, step, logs=message or '')
                self.stdout.write(f'   [{progress}%] {step}')

            # Train model
            self.stdout.write(f'Demarrage de l\'entrainement avec {algorithm}...')
            metrics = predictor.train(
                X, y,
                algorithm=algorithm,
                feature_names=feature_names,
                use_smote=len(unique) > 1 and min(counts) < len(X) * 0.3,  # Use SMOTE if imbalanced
                progress_callback=progress_callback
            )

            # Save model
            model_path = predictor.save_model()
            self.stdout.write(f'Modele sauvegarde: {model_path}')

            # Determine next version
            existing_versions = MLModel.objects.filter(
                name='DropoutRiskPredictor'
            ).values_list('version', flat=True)

            if existing_versions:
                max_version = max([int(v.split('.')[-1]) for v in existing_versions if v and '.' in v], default=0)
                new_version = f"1.0.{max_version + 1}"
            else:
                new_version = "1.0.0"

            # Create MLModel record
            # Metrics from train() are in 0-1 range, convert to 0-100 for storage
            # But check if they're already in 0-100 range
            accuracy_raw = float(metrics.get('accuracy', 0))
            precision_raw = float(metrics.get('precision', 0))
            recall_raw = float(metrics.get('recall', 0))
            f1_score_raw = float(metrics.get('f1_score', 0))
            
            # Convert to 0-100 if in 0-1 range
            accuracy_val = accuracy_raw * 100 if accuracy_raw <= 1.0 else accuracy_raw
            precision_val = precision_raw * 100 if precision_raw <= 1.0 else precision_raw
            recall_val = recall_raw * 100 if recall_raw <= 1.0 else recall_raw
            f1_score_val = f1_score_raw * 100 if f1_score_raw <= 1.0 else f1_score_raw
            
            # Ensure values are within 0-100 range
            accuracy_val = max(0.0, min(accuracy_val, 100.0))
            precision_val = max(0.0, min(precision_val, 100.0))
            recall_val = max(0.0, min(recall_val, 100.0))
            f1_score_val = max(0.0, min(f1_score_val, 100.0))
            
            ml_model = MLModel.objects.create(
                name='DropoutRiskPredictor',
                version=new_version,
                status=MLModel.Status.INACTIVE,
                accuracy=accuracy_val,
                precision=precision_val,
                recall=recall_val,
                f1_score=f1_score_val,
                trained_at=timezone.now(),
                training_data_size=len(X)
            )

            job.complete(ml_model)

            self.stdout.write(self.style.SUCCESS('\nEntrainement termine avec succes!'))
            self.stdout.write(f'Version du modele: {new_version}')
            self.stdout.write(f'Accuracy: {accuracy_val:.2f}%')
            self.stdout.write(f'Precision: {precision_val:.2f}%')
            self.stdout.write(f'Recall: {recall_val:.2f}%')
            self.stdout.write(f'F1-Score: {f1_score_val:.2f}%')

            self.stdout.write(f'\nPour activer ce modele, utilisez:')
            self.stdout.write(f'  python manage.py activate_model --version {new_version}')

        except Exception as e:
            job.fail(str(e))
            self.stdout.write(self.style.ERROR(f'\nErreur lors de l\'entrainement: {e}'))
            logger.exception("Training failed")
            raise

