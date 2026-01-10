from celery import shared_task
import logging
from django.utils import timezone
from .models import TrainingJob, MLModel
from .services import DropoutRiskPredictor, generate_synthetic_training_data

logger = logging.getLogger(__name__)

@shared_task
def run_training_job(job_id):
    """
    Celery task to run a training job in the background.
    """
    try:
        job = TrainingJob.objects.get(id=job_id)
        job.start()

        # Initialize predictor
        predictor = DropoutRiskPredictor()

        # Progress callback
        def progress_callback(progress, step, message=None):
            logs = f"{step}: {message}" if message else step
            job.update_progress(progress, step, logs)

        # Generate synthetic data and train
        # In a real scenario, we might want to use load_training_data_from_database()
        # depending on the job configuration.
        job.update_progress(5, "Génération des données d'entraînement...")

        # Check if we should use real data or synthetic
        # For now, we stick to synthetic as per original implementation,
        # but we could add a flag in job.hyperparameters
        X, y = generate_synthetic_training_data(n_samples=1000)

        job.update_progress(10, "Démarrage de l'entraînement...")

        metrics = predictor.train(
            X, y,
            algorithm=job.algorithm,
            hyperparameters=job.hyperparameters,
            progress_callback=progress_callback
        )

        # Save the trained model
        job.update_progress(95, "Sauvegarde du modèle...")
        model_path = predictor.save_model()

        # Determine next version
        existing_versions = MLModel.objects.filter(
            name='DropoutRiskPredictor'
        ).values_list('version', flat=True)

        if existing_versions:
            try:
                # Extract version numbers assuming format X.Y.Z
                versions = []
                for v in existing_versions:
                    try:
                        versions.append(tuple(map(int, v.split('.'))))
                    except ValueError:
                        continue

                if versions:
                    max_ver = max(versions)
                    new_version = f"{max_ver[0]}.{max_ver[1]}.{max_ver[2] + 1}"
                else:
                    new_version = "1.0.0"
            except Exception:
                new_version = f"1.0.{len(existing_versions)}"
        else:
            new_version = "1.0.0"

        # Create MLModel record
        ml_model = MLModel.objects.create(
            name='DropoutRiskPredictor',
            version=new_version,
            status=MLModel.Status.INACTIVE,
            accuracy=metrics['accuracy'],
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1_score=metrics['f1_score'],
            trained_at=timezone.now(),
            training_data_size=metrics['training_samples']
        )

        job.complete(ml_model)
        logger.info(f"Training job {job_id} completed successfully.")

    except TrainingJob.DoesNotExist:
        logger.error(f"Training job {job_id} not found.")
    except Exception as e:
        logger.exception(f"Training job {job_id} failed: {str(e)}")
        try:
            job = TrainingJob.objects.get(id=job_id)
            job.fail(str(e))
        except TrainingJob.DoesNotExist:
            pass
