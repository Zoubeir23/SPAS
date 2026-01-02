"""
Script to verify all Django models are properly configured.
Run with: python manage.py shell < scripts/verify_models.py
"""

import sys
from django.apps import apps

print("=" * 80)
print("VERIFICATION DES MODELES DJANGO - PROJET SPAS")
print("=" * 80)

# Liste des apps et leurs modèles attendus
EXPECTED_MODELS = {
    'students': ['Student'],
    'programs': ['Program', 'Subject'],
    'sessions': ['Session'],
    'grades': ['Grade'],
    'attendance': ['Attendance'],
    'users': ['User'],
    'ml': ['MLModel'],
    'predictions': ['Prediction'],
    'alerts': ['Alert'],
}

errors = []
warnings = []
success_count = 0

print("\n1. Vérification de l'existence des modèles...\n")

for app_label, expected_models in EXPECTED_MODELS.items():
    print(f"\nApp: {app_label}")
    print("-" * 40)

    try:
        app_config = apps.get_app_config(app_label)
    except LookupError:
        errors.append(f"App '{app_label}' not found in INSTALLED_APPS")
        print(f"  ❌ App non trouvée dans INSTALLED_APPS")
        continue

    for model_name in expected_models:
        try:
            model = apps.get_model(app_label, model_name)
            print(f"  ✓ {model_name}: {model._meta.db_table}")

            # Vérifier les champs
            field_count = len(model._meta.get_fields())
            print(f"    - {field_count} champs définis")

            # Vérifier les indexes
            index_count = len(model._meta.indexes)
            if index_count > 0:
                print(f"    - {index_count} index(es)")

            # Vérifier __str__ method
            if hasattr(model, '__str__'):
                print(f"    - Méthode __str__ définie")
            else:
                warnings.append(f"{app_label}.{model_name} n'a pas de méthode __str__")

            success_count += 1

        except LookupError:
            errors.append(f"Model '{model_name}' not found in app '{app_label}'")
            print(f"  ❌ {model_name}: Non trouvé")

print("\n" + "=" * 80)
print("2. Vérification des relations entre modèles...\n")

# Vérifier les relations ForeignKey importantes
EXPECTED_RELATIONS = [
    ('students.Student', 'program', 'programs.Program'),
    ('students.Student', 'session', 'sessions.Session'),
    ('grades.Grade', 'student', 'students.Student'),
    ('grades.Grade', 'subject', 'programs.Subject'),
    ('grades.Grade', 'session', 'sessions.Session'),
    ('attendance.Attendance', 'student', 'students.Student'),
    ('attendance.Attendance', 'subject', 'programs.Subject'),
    ('predictions.Prediction', 'student', 'students.Student'),
    ('predictions.Prediction', 'model_version', 'ml.MLModel'),
    ('alerts.Alert', 'student', 'students.Student'),
]

for model_path, field_name, related_model_path in EXPECTED_RELATIONS:
    try:
        app_label, model_name = model_path.split('.')
        model = apps.get_model(app_label, model_name)

        field = model._meta.get_field(field_name)
        related_model_str = f"{field.related_model._meta.app_label}.{field.related_model._meta.object_name}"

        if related_model_str == related_model_path:
            print(f"  ✓ {model_path}.{field_name} → {related_model_path}")
        else:
            errors.append(
                f"{model_path}.{field_name} pointe vers {related_model_str} "
                f"au lieu de {related_model_path}"
            )
            print(f"  ❌ {model_path}.{field_name} → {related_model_str} (attendu: {related_model_path})")

    except Exception as e:
        errors.append(f"Erreur lors de la vérification de {model_path}.{field_name}: {str(e)}")
        print(f"  ❌ {model_path}.{field_name}: {str(e)}")

print("\n" + "=" * 80)
print("3. Vérification des choix (TextChoices)...\n")

# Vérifier que les modèles utilisent bien les bonnes valeurs de choix
EXPECTED_CHOICES = [
    ('students.Student', 'status', ['active', 'inactive', 'graduated']),
    ('students.Student', 'risk_level', ['low', 'medium', 'high']),
    ('programs.Program', 'status', ['active', 'inactive']),
    ('sessions.Session', 'status', ['active', 'inactive', 'completed']),
    ('grades.Grade', 'type', ['exam', 'assignment', 'project', 'participation']),
    ('attendance.Attendance', 'status', ['present', 'absent', 'late', 'excused']),
    ('users.User', 'role', ['admin', 'teacher', 'ds', 'pedagogical']),
    ('ml.MLModel', 'status', ['active', 'inactive', 'training']),
    ('predictions.Prediction', 'risk_level', ['low', 'medium', 'high', 'critical']),
    ('alerts.Alert', 'type', ['performance', 'attendance', 'risk', 'prediction']),
    ('alerts.Alert', 'level', ['low', 'medium', 'high', 'critical']),
    ('alerts.Alert', 'status', ['new', 'acknowledged', 'resolved']),
]

for model_path, field_name, expected_values in EXPECTED_CHOICES:
    try:
        app_label, model_name = model_path.split('.')
        model = apps.get_model(app_label, model_name)
        field = model._meta.get_field(field_name)

        if hasattr(field, 'choices') and field.choices:
            actual_values = [choice[0] for choice in field.choices]
            if set(actual_values) == set(expected_values):
                print(f"  ✓ {model_path}.{field_name}: {len(actual_values)} choix")
            else:
                missing = set(expected_values) - set(actual_values)
                extra = set(actual_values) - set(expected_values)
                if missing:
                    warnings.append(f"{model_path}.{field_name} manque: {missing}")
                if extra:
                    warnings.append(f"{model_path}.{field_name} a en trop: {extra}")
                print(f"  ⚠ {model_path}.{field_name}: Choix différents")
        else:
            warnings.append(f"{model_path}.{field_name} n'a pas de choix définis")
            print(f"  ⚠ {model_path}.{field_name}: Pas de choix")

    except Exception as e:
        warnings.append(f"Erreur lors de la vérification de {model_path}.{field_name}: {str(e)}")
        print(f"  ⚠ {model_path}.{field_name}: {str(e)}")

print("\n" + "=" * 80)
print("RÉSUMÉ")
print("=" * 80)

print(f"\n✓ Modèles vérifiés avec succès: {success_count}")

if warnings:
    print(f"\n⚠ Avertissements: {len(warnings)}")
    for warning in warnings:
        print(f"  - {warning}")

if errors:
    print(f"\n❌ Erreurs: {len(errors)}")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("\n✓ Tous les modèles sont correctement configurés!")
    print("\nProchaines étapes:")
    print("  1. python manage.py makemigrations")
    print("  2. python manage.py migrate")
    print("  3. python manage.py createsuperuser")
    sys.exit(0)
