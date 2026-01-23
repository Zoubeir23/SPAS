"""
Django management command to reset application data.

Usage:
    python manage.py reset_app

This command will:
- Delete all business data (students, grades, attendance, predictions, alerts, interventions)
- Keep user accounts (admin, staff)
- Clean media files (student photos, ML models)
- Display confirmation summary
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
import os
import shutil


class Command(BaseCommand):
    help = 'Reset application data while preserving user accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        # Display warning
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('⚠️  ATTENTION : REMISE À ZÉRO DE L\'APPLICATION'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('\nCette opération va supprimer :')
        self.stdout.write('  ✓ Tous les étudiants')
        self.stdout.write('  ✓ Toutes les notes')
        self.stdout.write('  ✓ Toutes les absences')
        self.stdout.write('  ✓ Toutes les prédictions')
        self.stdout.write('  ✓ Toutes les alertes et interventions')
        self.stdout.write('  ✓ Tous les modèles ML et jobs d\'entraînement')
        self.stdout.write('  ✓ Tous les fichiers média (photos, modèles)')
        self.stdout.write('\n⚠️  Les comptes utilisateurs seront PRÉSERVÉS\n')

        # Confirmation prompt
        if not options['force']:
            confirm = input('Continuer ? Tapez "RESET" pour confirmer : ')
            if confirm != 'RESET':
                self.stdout.write(self.style.ERROR('❌ Opération annulée.'))
                return

        self.stdout.write('\n🔄 Démarrage du nettoyage...\n')

        # Import models here to avoid AppRegistryNotReady
        from apps.students.models import Student
        from apps.grades.models import Grade
        from apps.attendance.models import Attendance
        from apps.predictions.models import Prediction
        from apps.alerts.models import Alert, Intervention
        from apps.ml.models import MLModel, TrainingJob
        from apps.sessions.models import Session
        from apps.programs.models import Program, Department, Subject

        deleted_counts = {}

        try:
            with transaction.atomic():
                # Delete in correct order (respecting foreign keys)

                # 1. Interventions (depends on alerts and students)
                self.stdout.write('🗑️  Suppression des interventions...')
                count = Intervention.objects.all().count()
                Intervention.objects.all().delete()
                deleted_counts['Interventions'] = count
                self.stdout.write(self.style.SUCCESS(f'   ✓ {count} interventions supprimées'))

                # 2. Alerts (depends on students and predictions)
                self.stdout.write('🗑️  Suppression des alertes...')
                count = Alert.objects.all().count()
                Alert.objects.all().delete()
                deleted_counts['Alertes'] = count
                self.stdout.write(self.style.SUCCESS(f'   ✓ {count} alertes supprimées'))

                # 3. Predictions (depends on students and ML models)
                self.stdout.write('🗑️  Suppression des prédictions...')
                count = Prediction.objects.all().count()
                Prediction.objects.all().delete()
                deleted_counts['Prédictions'] = count
                self.stdout.write(self.style.SUCCESS(f'   ✓ {count} prédictions supprimées'))

                # 4. Grades (depends on students)
                self.stdout.write('🗑️  Suppression des notes...')
                count = Grade.objects.all().count()
                Grade.objects.all().delete()
                deleted_counts['Notes'] = count
                self.stdout.write(self.style.SUCCESS(f'   ✓ {count} notes supprimées'))

                # 5. Attendance (depends on students)
                self.stdout.write('🗑️  Suppression des absences...')
                count = Attendance.objects.all().count()
                Attendance.objects.all().delete()
                deleted_counts['Absences'] = count
                self.stdout.write(self.style.SUCCESS(f'   ✓ {count} absences supprimées'))

                # 6. Students
                self.stdout.write('🗑️  Suppression des étudiants...')
                count = Student.objects.all().count()
                Student.objects.all().delete()
                deleted_counts['Étudiants'] = count
                self.stdout.write(self.style.SUCCESS(f'   ✓ {count} étudiants supprimés'))

                # 7. Training Jobs (before ML models)
                self.stdout.write('🗑️  Suppression des jobs d\'entraînement...')
                count = TrainingJob.objects.all().count()
                TrainingJob.objects.all().delete()
                deleted_counts['Jobs entraînement'] = count
                self.stdout.write(self.style.SUCCESS(f'   ✓ {count} jobs supprimés'))

                # 8. ML Models
                self.stdout.write('🗑️  Suppression des modèles ML...')
                count = MLModel.objects.all().count()
                MLModel.objects.all().delete()
                deleted_counts['Modèles ML'] = count
                self.stdout.write(self.style.SUCCESS(f'   ✓ {count} modèles supprimés'))

                # Optional: Reset sessions, programs, departments (if needed)
                # Uncomment if you want to also delete these
                # self.stdout.write('🗑️  Suppression des sessions académiques...')
                # count = Session.objects.all().count()
                # Session.objects.all().delete()
                # deleted_counts['Sessions'] = count

            self.stdout.write(self.style.SUCCESS('\n✅ Données métier supprimées avec succès\n'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erreur lors de la suppression : {str(e)}'))
            return

        # Clean media files
        self.stdout.write('📁 Nettoyage des fichiers média...\n')
        media_cleaned = self._clean_media_files()

        # Display summary
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ APPLICATION REMISE À ZÉRO AVEC SUCCÈS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        self.stdout.write('\n📊 Résumé des suppressions :')
        total = 0
        for model, count in deleted_counts.items():
            self.stdout.write(f'  • {model:<25} : {count:>6}')
            total += count

        self.stdout.write(self.style.SUCCESS(f'\n  {"TOTAL":<25} : {total:>6} enregistrements supprimés'))

        if media_cleaned:
            self.stdout.write('\n📁 Fichiers média nettoyés :')
            for path in media_cleaned:
                self.stdout.write(f'  • {path}')

        self.stdout.write(self.style.WARNING('\n⚠️  Les comptes utilisateurs ont été PRÉSERVÉS'))
        self.stdout.write(self.style.SUCCESS('\n🎉 Votre application est maintenant vierge et prête pour la démo !\n'))

    def _clean_media_files(self):
        """Clean media files (student photos, ML models)."""
        cleaned_paths = []
        media_root = settings.MEDIA_ROOT

        if not os.path.exists(media_root):
            self.stdout.write(self.style.WARNING('   ⚠️  Dossier media non trouvé, ignoré'))
            return cleaned_paths

        # Directories to clean
        dirs_to_clean = [
            ('student_photos', 'Photos de profil'),
            ('ml_models', 'Modèles ML'),
        ]

        for dir_name, display_name in dirs_to_clean:
            dir_path = os.path.join(media_root, dir_name)
            if os.path.exists(dir_path):
                try:
                    # Count files before deletion
                    files_count = sum(len(files) for _, _, files in os.walk(dir_path))

                    # Remove directory
                    shutil.rmtree(dir_path)

                    # Recreate empty directory
                    os.makedirs(dir_path)

                    # Add .gitkeep to preserve directory in git
                    gitkeep_path = os.path.join(dir_path, '.gitkeep')
                    with open(gitkeep_path, 'w') as f:
                        f.write('')

                    self.stdout.write(self.style.SUCCESS(f'   ✓ {display_name} : {files_count} fichiers supprimés'))
                    cleaned_paths.append(f'{display_name} ({dir_name}/)')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Erreur nettoyage {display_name} : {str(e)}'))

        return cleaned_paths
