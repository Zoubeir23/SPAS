#!/usr/bin/env python
"""
Script pour mettre à jour les départements et filières avec les vraies données ISI
"""
import os
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

import django
django.setup()

from apps.programs.models import Department, Program
from apps.students.models import Student

def main():
    print("=== Mise à jour des départements et filières ISI ===\n")
    
    # Créer les vrais départements ISI
    departments_data = [
        ('DGI', 'Génie Informatique'),
        ('DRS', 'Réseaux et Systèmes'),
        ('DGM', 'Gestion et Management'),
    ]
    
    departments = {}
    for code, name in departments_data:
        dept, created = Department.objects.update_or_create(
            code=code,
            defaults={'name': name, 'status': 'active'}
        )
        departments[code] = dept
        status = 'Créé' if created else 'Mis à jour'
        print(f"  [{status}] Département: {code} - {name}")
    
    print(f"\n✓ Départements: {len(departments)}\n")
    
    # Créer les vraies filières ISI (sans les niveaux)
    programs_data = [
        # Génie Informatique - Licences (durée 3 ans)
        {'code': 'INFO-MUL', 'name': 'Infographie / Multimédia', 'dept': 'DGI', 'duration': 3},
        {'code': 'DS-BD', 'name': 'Data Science & Big Data', 'dept': 'DGI', 'duration': 3},
        {'code': 'MKT-DIG', 'name': 'Marketing Digital', 'dept': 'DGI', 'duration': 3},
        {'code': 'GEO-DEV', 'name': 'Géomatique et Développement d\'Applications', 'dept': 'DGI', 'duration': 3},
        {'code': 'GL', 'name': 'Génie Logiciel', 'dept': 'DGI', 'duration': 3},
        {'code': 'IG', 'name': 'Informatique de Gestion', 'dept': 'DGI', 'duration': 3},
        # Génie Informatique - Masters (durée 2 ans)
        {'code': 'M-GL', 'name': 'Master Génie Logiciel', 'dept': 'DGI', 'duration': 2},
        {'code': 'M-IAGE', 'name': 'Master Informatique Appliquée à la Gestion', 'dept': 'DGI', 'duration': 2},
        {'code': 'DITI', 'name': 'Ingénieur en Techniques Informatiques (DITI)', 'dept': 'DGI', 'duration': 5},
        
        # Réseaux et Systèmes - Licences (durée 3 ans)
        {'code': 'RI', 'name': 'Réseaux Informatiques', 'dept': 'DRS', 'duration': 3},
        {'code': 'RT', 'name': 'Réseaux Télécoms', 'dept': 'DRS', 'duration': 3},
        {'code': 'CYBER', 'name': 'Cyber-sécurité', 'dept': 'DRS', 'duration': 3},
        {'code': 'SE-IOT', 'name': 'Systèmes Embarqués & IoT', 'dept': 'DRS', 'duration': 3},
        # Réseaux et Systèmes - Masters (durée 2 ans)
        {'code': 'M-RSI', 'name': 'Master Réseaux et Systèmes Informatiques', 'dept': 'DRS', 'duration': 2},
        {'code': 'M-VCC', 'name': 'Master Virtualisation et Cloud Computing', 'dept': 'DRS', 'duration': 2},
        {'code': 'M-RT', 'name': 'Master Réseaux Télécommunications', 'dept': 'DRS', 'duration': 2},
        {'code': 'M-SSI', 'name': 'Master Sécurité des Systèmes d\'Informations', 'dept': 'DRS', 'duration': 2},
        
        # Gestion et Management - Licences (durée 3 ans)
        {'code': 'BFA', 'name': 'Banque Finance Assurance', 'dept': 'DGM', 'duration': 3},
        {'code': 'FC', 'name': 'Finance et Comptabilité', 'dept': 'DGM', 'duration': 3},
        {'code': 'CI', 'name': 'Commerce International', 'dept': 'DGM', 'duration': 3},
        {'code': 'AD', 'name': 'Assistanat de Direction', 'dept': 'DGM', 'duration': 3},
        # Gestion et Management - Masters (durée 2 ans)
        {'code': 'M-FIN', 'name': 'Master Finance', 'dept': 'DGM', 'duration': 2},
        {'code': 'M-BA', 'name': 'Master Banque Assurance', 'dept': 'DGM', 'duration': 2},
    ]
    
    new_programs = {}
    for p in programs_data:
        prog, created = Program.objects.update_or_create(
            code=p['code'],
            defaults={
                'name': p['name'],
                'department': departments[p['dept']],
                'duration': p['duration'],
                'status': 'active'
            }
        )
        new_programs[p['code']] = prog
        status = 'Créé' if created else 'Mis à jour'
        print(f"  [{status}] {p['code']}: {p['name']} ({p['dept']})")
    
    print(f"\n✓ Filières créées/mises à jour: {len(new_programs)}\n")
    
    # Réassigner les étudiants vers les nouvelles filières appropriées
    # Mapper les anciens programmes vers les nouveaux
    program_mapping = {
        # Anciens codes vers nouveaux codes
        'INFO': 'IG',
        'L-INFO': 'IG',
        'M-DS': 'DS-BD',
        'DS-L1': 'DS-BD',
        'DS-L2': 'DS-BD',
        'DS-L3': 'DS-BD',
        'DS-M1': 'DS-BD',
        'GL-L1': 'GL',
        'GL-L2': 'GL',
        'GL-L3': 'GL',
        'GL-M1': 'M-GL',
        'L-RES': 'RI',
    }
    
    # Obtenir une filière par défaut pour les étudiants sans correspondance
    default_program = new_programs.get('GL') or list(new_programs.values())[0]
    
    # Réassigner les étudiants
    students_updated = 0
    for student in Student.objects.select_related('program').all():
        old_code = student.program.code if student.program else None
        
        if old_code and old_code in new_programs:
            # Le programme existe déjà avec le bon code
            continue
        elif old_code and old_code in program_mapping:
            # Mapper vers le nouveau programme
            new_code = program_mapping[old_code]
            if new_code in new_programs:
                student.program = new_programs[new_code]
                student.save()
                students_updated += 1
        else:
            # Assigner au programme par défaut
            student.program = default_program
            student.save()
            students_updated += 1
    
    print(f"✓ Étudiants réassignés: {students_updated}")
    
    # Supprimer les anciens programmes non utilisés
    old_programs = Program.objects.exclude(code__in=new_programs.keys())
    old_count = old_programs.count()
    
    # Vérifier si des étudiants utilisent encore ces programmes
    for prog in old_programs:
        if not Student.objects.filter(program=prog).exists():
            prog.delete()
    
    print(f"✓ Anciens programmes supprimés: {old_count}")
    
    # Supprimer les anciens départements non utilisés
    old_depts = Department.objects.exclude(code__in=departments.keys())
    for dept in old_depts:
        if not Program.objects.filter(department=dept).exists():
            dept.delete()
    
    print("\n=== Résumé final ===")
    print(f"Départements: {Department.objects.count()}")
    print(f"Filières: {Program.objects.count()}")
    print(f"Étudiants: {Student.objects.count()}")
    
    # Afficher la répartition
    print("\n=== Répartition des étudiants par filière ===")
    from django.db.models import Count
    for dept in Department.objects.all():
        print(f"\n{dept.name}:")
        for prog in Program.objects.filter(department=dept).annotate(student_count=Count('students')):
            print(f"  - {prog.name}: {prog.student_count} étudiant(s)")

if __name__ == '__main__':
    main()
