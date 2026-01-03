"""
Management command to create ISI departments and programs based on the catalog.
"""
from django.core.management.base import BaseCommand
from apps.programs.models import Department, Program


class Command(BaseCommand):
    help = 'Create ISI departments and programs from the catalog'

    def handle(self, *args, **options):
        self.stdout.write('Creation des departements et filieres ISI...')

        # Créer les départements
        dept_reseaux, created = Department.objects.get_or_create(
            code='DRS',
            defaults={
                'name': 'Département Réseaux et Systèmes',
                'description': 'Département spécialisé en réseaux informatiques et systèmes',
                'status': 'active'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'[OK] Departement cree: {dept_reseaux.name}'))
        else:
            self.stdout.write(f'  Departement existe deja: {dept_reseaux.name}')

        dept_genie, created = Department.objects.get_or_create(
            code='DGI',
            defaults={
                'name': 'Département Génie Informatique',
                'description': 'Département spécialisé en génie logiciel, data science et marketing digital',
                'status': 'active'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'[OK] Departement cree: {dept_genie.name}'))
        else:
            self.stdout.write(f'  Departement existe deja: {dept_genie.name}')

        dept_elearning, created = Department.objects.get_or_create(
            code='DELE',
            defaults={
                'name': 'Groupe ISI En Ligne E-Learning',
                'description': 'Département spécialisé dans la formation en ligne',
                'status': 'active'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'[OK] Departement cree: {dept_elearning.name}'))
        else:
            self.stdout.write(f'  Departement existe deja: {dept_elearning.name}')

        # Créer les filières pour Département Réseaux et Systèmes
        # Selon le catalogue: Réseaux Informatiques (L1, L2, L3, Master)
        programs_reseaux = [
            {'code': 'RES-L1', 'name': 'Réseaux Informatiques - Licence 1', 'duration': 1},
            {'code': 'RES-L2', 'name': 'Réseaux Informatiques - Licence 2', 'duration': 1},
            {'code': 'RES-L3', 'name': 'Réseaux Informatiques - Licence Professionnelle', 'duration': 1},
            {'code': 'RES-M1', 'name': 'Réseaux Informatiques - Master Professionnel', 'duration': 2},
        ]

        # Créer les filières pour Département Génie Informatique
        # Selon le catalogue: Génie Logiciel, Data Science & Big Data, Marketing Digital (L1, L2, L3, Master)
        # + D.I.T.I (Diplôme d'Ingénieur en Techniques Informatiques) BAC +5
        programs_genie = [
            # Génie Logiciel
            {'code': 'GL-L1', 'name': 'Génie Logiciel - Licence 1', 'duration': 1},
            {'code': 'GL-L2', 'name': 'Génie Logiciel - Licence 2', 'duration': 1},
            {'code': 'GL-L3', 'name': 'Génie Logiciel - Licence Professionnelle', 'duration': 1},
            {'code': 'GL-M1', 'name': 'Génie Logiciel - Master Professionnel', 'duration': 2},
            # Data Science & Big Data
            {'code': 'DS-L1', 'name': 'Data Science & Big Data - Licence 1', 'duration': 1},
            {'code': 'DS-L2', 'name': 'Data Science & Big Data - Licence 2', 'duration': 1},
            {'code': 'DS-L3', 'name': 'Data Science & Big Data - Licence Professionnelle', 'duration': 1},
            {'code': 'DS-M1', 'name': 'Data Science & Big Data - Master Professionnel', 'duration': 2},
            # Marketing Digital
            {'code': 'MD-L1', 'name': 'Marketing Digital - Licence 1', 'duration': 1},
            {'code': 'MD-L2', 'name': 'Marketing Digital - Licence 2', 'duration': 1},
            {'code': 'MD-L3', 'name': 'Marketing Digital - Licence Professionnelle', 'duration': 1},
            {'code': 'MD-M1', 'name': 'Marketing Digital - Master Professionnel', 'duration': 2},
            # D.I.T.I (Diplôme d'Ingénieur en Techniques Informatiques) BAC +5
            {'code': 'DITI', 'name': 'Diplôme d\'Ingénieur en Techniques Informatiques (D.I.T.I) BAC +5', 'duration': 5},
        ]

        # Créer les filières pour E-Learning
        # Selon le catalogue: Réseaux Informatiques, Génie Logiciel, Finance et Comptabilité (L3, Master)
        programs_elearning = [
            {'code': 'EL-RES-L3', 'name': 'Réseaux Informatiques - Licence Professionnelle (E-Learning)', 'duration': 1},
            {'code': 'EL-RES-M1', 'name': 'Réseaux Informatiques - Master Professionnel (E-Learning)', 'duration': 2},
            {'code': 'EL-GL-L3', 'name': 'Génie Logiciel - Licence Professionnelle (E-Learning)', 'duration': 1},
            {'code': 'EL-GL-M1', 'name': 'Génie Logiciel - Master Professionnel (E-Learning)', 'duration': 2},
            {'code': 'EL-FC-L3', 'name': 'Finance et Comptabilité - Licence Professionnelle (E-Learning)', 'duration': 1},
            {'code': 'EL-FC-M1', 'name': 'Finance et Comptabilité - Master Professionnel (E-Learning)', 'duration': 2},
        ]

        # Créer les filières
        created_count = 0
        for prog_data in programs_reseaux:
            program, created = Program.objects.get_or_create(
                code=prog_data['code'],
                defaults={
                    'name': prog_data['name'],
                    'duration': prog_data['duration'],
                    'department': dept_reseaux,
                    'status': 'active'
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Filiere creee: {program.name}'))
            else:
                # Mettre à jour le département si nécessaire
                if program.department != dept_reseaux:
                    program.department = dept_reseaux
                    program.save()
                    self.stdout.write(f'  [UPDATE] Filiere mise a jour: {program.name}')

        for prog_data in programs_genie:
            program, created = Program.objects.get_or_create(
                code=prog_data['code'],
                defaults={
                    'name': prog_data['name'],
                    'duration': prog_data['duration'],
                    'department': dept_genie,
                    'status': 'active'
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Filiere creee: {program.name}'))
            else:
                # Mettre à jour le département si nécessaire
                if program.department != dept_genie:
                    program.department = dept_genie
                    program.save()
                    self.stdout.write(f'  [UPDATE] Filiere mise a jour: {program.name}')

        for prog_data in programs_elearning:
            program, created = Program.objects.get_or_create(
                code=prog_data['code'],
                defaults={
                    'name': prog_data['name'],
                    'duration': prog_data['duration'],
                    'department': dept_elearning,
                    'status': 'active'
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] Filiere creee: {program.name}'))
            else:
                # Mettre à jour le département si nécessaire
                if program.department != dept_elearning:
                    program.department = dept_elearning
                    program.save()
                    self.stdout.write(f'  [UPDATE] Filiere mise a jour: {program.name}')

        self.stdout.write(self.style.SUCCESS(f'\n[OK] Termine ! {created_count} filiere(s) creee(s).'))

