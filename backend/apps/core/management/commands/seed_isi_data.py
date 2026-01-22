"""
Django management command to seed ISI (Groupe ISI) official departments and programs.

Usage:
    python manage.py seed_isi_data

This command creates:
- Official ISI departments (4 departments)
- Official ISI programs/filières (13 programs)
- Based on real data from groupeisi.com
"""
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Seed database with official ISI departments and programs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force seed even if data already exists',
        )

    def handle(self, *args, **options):
        # Import models here to avoid AppRegistryNotReady
        from apps.programs.models import Department, Program

        # Display header
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('📚 SEED ISI DATA - Groupe ISI Official Structure'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('\nSource: groupeisi.com')
        self.stdout.write('Données officielles 2024-2025\n')

        # Check if data already exists
        dept_count = Department.objects.count()
        program_count = Program.objects.count()

        if (dept_count > 0 or program_count > 0) and not options['force']:
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  Des données existent déjà ({dept_count} départements, {program_count} filières).'
            ))
            confirm = input('Continuer quand même ? (o/N) : ')
            if confirm.lower() != 'o':
                self.stdout.write(self.style.ERROR('❌ Opération annulée.'))
                return

        self.stdout.write('\n🔄 Création des départements et filières ISI...\n')

        try:
            with transaction.atomic():
                # Official ISI Departments & Programs (Source: groupeisi.com)
                departments_data = [
                    {
                        'code': 'DGI',
                        'name': 'Génie Informatique',
                        'description': 'Département de Génie Informatique - Formation en développement logiciel, infographie, et géomatique',
                        'programs': [
                            {
                                'code': 'GL',
                                'name': 'Génie Logiciel',
                                'description': 'Formation en conception et développement de logiciels, architecture applicative et ingénierie des systèmes',
                                'duration': 5  # Licence 3 ans + Master 2 ans
                            },
                            {
                                'code': 'IM',
                                'name': 'Infographie et Multimédia',
                                'description': 'Formation en design graphique, animation 3D, montage vidéo et création multimédia',
                                'duration': 3
                            },
                            {
                                'code': 'GDA',
                                'name': 'Géomatique et Développement d\'applications',
                                'description': 'Formation en systèmes d\'information géographique (SIG), cartographie numérique et applications géospatiales',
                                'duration': 3
                            },
                        ]
                    },
                    {
                        'code': 'DRS',
                        'name': 'Réseaux et Systèmes',
                        'description': 'Département de Réseaux et Systèmes - Formation en infrastructure réseau, télécoms, cybersécurité et IoT',
                        'programs': [
                            {
                                'code': 'RI',
                                'name': 'Réseaux Informatiques',
                                'description': 'Formation en administration réseaux, routage, switching et infrastructure IT',
                                'duration': 3
                            },
                            {
                                'code': 'RT',
                                'name': 'Réseaux Télécommunications',
                                'description': 'Formation en télécommunications, réseaux mobiles, VoIP et technologies sans fil',
                                'duration': 3
                            },
                            {
                                'code': 'CS',
                                'name': 'Cyber Sécurité',
                                'description': 'Formation en sécurité des systèmes d\'information, ethical hacking, et défense informatique',
                                'duration': 3
                            },
                            {
                                'code': 'SEIOT',
                                'name': 'Systèmes Embarqués et IoT',
                                'description': 'Formation en systèmes embarqués, Internet des objets (IoT), programmation microcontrôleurs et électronique',
                                'duration': 3
                            },
                        ]
                    },
                    {
                        'code': 'DGM',
                        'name': 'Gestion & Management',
                        'description': 'Département de Gestion & Management - Formation en finance, commerce international et banque-assurance',
                        'programs': [
                            {
                                'code': 'FC',
                                'name': 'Finance & Comptabilité',
                                'description': 'Formation en comptabilité générale, audit, contrôle de gestion et finance d\'entreprise',
                                'duration': 3
                            },
                            {
                                'code': 'CI',
                                'name': 'Commerce International',
                                'description': 'Formation en commerce international, logistique, import-export et marketing global',
                                'duration': 3
                            },
                            {
                                'code': 'BFA',
                                'name': 'Banque Finance Assurance',
                                'description': 'Formation en services bancaires, produits financiers, assurance et gestion de patrimoine',
                                'duration': 3
                            },
                        ]
                    },
                    {
                        'code': 'DIAD',
                        'name': 'IA & Data',
                        'description': 'Département Intelligence Artificielle & Data - Formation en data science, machine learning et big data',
                        'programs': [
                            {
                                'code': 'DSBD',
                                'name': 'Data Science & Big Data Technology',
                                'description': 'Formation en science des données, machine learning, deep learning, analyse prédictive et big data',
                                'duration': 5  # Licence 3 ans + Master 2 ans
                            },
                        ]
                    },
                ]

                dept_created = 0
                prog_created = 0

                for dept_data in departments_data:
                    programs = dept_data.pop('programs')

                    # Create or get department
                    department, created = Department.objects.get_or_create(
                        code=dept_data['code'],
                        defaults={
                            'name': dept_data['name'],
                            'description': dept_data['description'],
                            'status': 'active'
                        }
                    )

                    if created:
                        dept_created += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'  ✓ Département créé: {department.code} - {department.name}'
                        ))
                    else:
                        self.stdout.write(
                            f'  • Département existant: {department.code} - {department.name}'
                        )

                    # Create programs for this department
                    for prog_data in programs:
                        program, prog_was_created = Program.objects.get_or_create(
                            code=prog_data['code'],
                            defaults={
                                'name': prog_data['name'],
                                'description': prog_data['description'],
                                'duration': prog_data['duration'],
                                'department': department,
                                'status': 'active'
                            }
                        )

                        if prog_was_created:
                            prog_created += 1
                            self.stdout.write(self.style.SUCCESS(
                                f'    ✓ Filière créée: {program.code} - {program.name}'
                            ))
                        else:
                            # Update department if program exists but without department
                            if not program.department:
                                program.department = department
                                program.save(update_fields=['department'])
                                self.stdout.write(
                                    f'    • Filière mise à jour: {program.code} - {program.name}'
                                )
                            else:
                                self.stdout.write(
                                    f'    • Filière existante: {program.code} - {program.name}'
                                )

            # Display summary
            self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
            self.stdout.write(self.style.SUCCESS('✅ SEED ISI DATA TERMINÉ AVEC SUCCÈS'))
            self.stdout.write(self.style.SUCCESS('=' * 70))

            self.stdout.write('\n📊 Résumé :')
            self.stdout.write(f'  • Départements créés     : {dept_created}')
            self.stdout.write(f'  • Filières créées        : {prog_created}')
            self.stdout.write(f'  • Total départements     : {Department.objects.count()}')
            self.stdout.write(f'  • Total filières         : {Program.objects.count()}')

            self.stdout.write(self.style.WARNING('\n⚠️  Vérifiez les données dans l\'interface d\'administration'))
            self.stdout.write(self.style.SUCCESS('\n🎉 Votre base est maintenant conforme à la structure ISI !\n'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erreur lors du seed : {str(e)}'))
            raise
