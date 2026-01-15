"""
Django management command to activate an ML model version.
"""
import sys
from django.core.management.base import BaseCommand
from apps.ml.models import MLModel

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


class Command(BaseCommand):
    help = 'Activate an ML model version'

    def add_arguments(self, parser):
        parser.add_argument(
            'model_version',
            type=str,
            nargs='?',
            help='Model version to activate (e.g., 1.0.4)'
        )
        parser.add_argument(
            '--model-version',
            type=str,
            dest='model_version_alt',
            help='Model version to activate (alternative)'
        )

    def handle(self, *args, **options):
        version = options.get('model_version') or options.get('model_version_alt')
        
        if not version:
            self.stdout.write(self.style.ERROR('Version du modele requise'))
            self.stdout.write('Usage: python manage.py activate_model <version>')
            self.stdout.write('Exemple: python manage.py activate_model 1.0.4')
            return

        try:
            model = MLModel.objects.get(version=version)
            
            # Activate the model
            model.activate()
            
            self.stdout.write(self.style.SUCCESS(f'Modele {version} active avec succes!'))
            self.stdout.write(f'  Nom: {model.name}')
            self.stdout.write(f'  Accuracy: {model.accuracy}%')
            self.stdout.write(f'  Precision: {model.precision}%')
            self.stdout.write(f'  Recall: {model.recall}%')
            self.stdout.write(f'  F1-Score: {model.f1_score}%')
            
        except MLModel.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Modele version {version} non trouve'))
            self.stdout.write('Versions disponibles:')
            for m in MLModel.objects.all().order_by('-trained_at'):
                self.stdout.write(f'  - {m.version} ({m.status})')
            return

