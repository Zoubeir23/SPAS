#!/usr/bin/env python3
"""
Script de Test Django - Validation Backend
===========================================
Teste que Django est correctement configuré pour la soutenance.

Usage: python backend_check.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Couleurs
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}{text.center(70)}{RESET}")
    print(f"{BOLD}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def check_env_file():
    """Vérifie que le fichier .env existe."""
    print_header("1️⃣  VÉRIFICATION FICHIER .ENV")

    env_file = BASE_DIR / '.env'
    env_example = BASE_DIR / '.env.example'

    if env_file.exists():
        print_success(f".env trouvé : {env_file}")
        return True
    else:
        print_error(f".env non trouvé : {env_file}")
        if env_example.exists():
            print_warning(f"Fichier .env.example trouvé : {env_example}")
            print_warning(f"Créez .env depuis .env.example : cp {env_example} {env_file}")
        return False

def check_django_import():
    """Vérifie que Django peut être importé."""
    print_header("2️⃣  VÉRIFICATION IMPORT DJANGO")

    try:
        import django
        print_success(f"Django importé : version {django.get_version()}")
        return True
    except ImportError as e:
        print_error(f"Impossible d'importer Django : {e}")
        print_warning("Installez les dépendances : pip install -r backend/requirements.txt")
        return False

def check_django_setup():
    """Vérifie que Django peut être configuré."""
    print_header("3️⃣  CONFIGURATION DJANGO")

    try:
        django.setup()
        print_success("Django configuré avec succès")
        return True
    except Exception as e:
        print_error(f"Erreur de configuration Django : {e}")
        return False

def check_models():
    """Vérifie que les modèles principaux existent."""
    print_header("4️⃣  VÉRIFICATION MODÈLES")

    try:
        from apps.users.models import User
        from apps.students.models import Student
        from apps.predictions.models import Prediction

        print_success("User model importé")
        print_success("Student model importé")
        print_success("Prediction model importé")

        # Vérifier RiskLevel
        if hasattr(Student, 'RiskLevel'):
            risk_levels = [choice[0] for choice in Student.RiskLevel.choices]
            if 'critical' in risk_levels:
                print_success(f"Student.RiskLevel contient 'critical' : {risk_levels}")
            else:
                print_error(f"Student.RiskLevel manque 'critical' : {risk_levels}")

        return True
    except ImportError as e:
        print_error(f"Erreur d'import de modèles : {e}")
        return False

def check_database():
    """Vérifie la connexion à la base de données."""
    print_header("5️⃣  VÉRIFICATION BASE DE DONNÉES")

    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print_success("Connexion à la base de données OK")

        # Vérifier les migrations
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        try:
            call_command('showmigrations', '--plan', stdout=out)
            migrations = out.getvalue()
            if '[ ]' in migrations:
                print_warning("Migrations non appliquées détectées")
                print_warning("Lancez : python manage.py migrate")
            else:
                print_success("Toutes les migrations sont appliquées")
        except Exception as e:
            print_warning(f"Impossible de vérifier les migrations : {e}")

        return True
    except Exception as e:
        print_error(f"Erreur de connexion à la base de données : {e}")
        print_warning("Lancez : python manage.py migrate")
        return False

def check_permissions():
    """Vérifie que les permissions RBAC sont correctes."""
    print_header("6️⃣  VÉRIFICATION PERMISSIONS RBAC")

    try:
        from apps.users.views import UserViewSet
        from apps.core.views import system_settings

        # Vérifier UserViewSet.get_permissions
        viewset = UserViewSet()
        viewset.action = 'list'
        permissions = viewset.get_permissions()

        from rest_framework.permissions import IsAdminUser
        if any(isinstance(p, IsAdminUser) for p in permissions):
            print_success("UserViewSet.list nécessite IsAdminUser ✅")
        else:
            print_error("UserViewSet.list ne nécessite PAS IsAdminUser ❌")

        # Vérifier 'me' endpoint
        viewset.action = 'me'
        permissions = viewset.get_permissions()

        from rest_framework.permissions import IsAuthenticated
        if any(isinstance(p, IsAuthenticated) for p in permissions):
            print_success("UserViewSet.me accessible à IsAuthenticated ✅")

        return True
    except Exception as e:
        print_error(f"Erreur de vérification des permissions : {e}")
        return False

def check_settings_security():
    """Vérifie les paramètres de sécurité."""
    print_header("7️⃣  VÉRIFICATION SÉCURITÉ SETTINGS")

    try:
        from django.conf import settings

        # FILE_UPLOAD_MAX_MEMORY_SIZE
        if hasattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE'):
            size_mb = settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024)
            print_success(f"FILE_UPLOAD_MAX_MEMORY_SIZE = {size_mb:.1f} MB")
        else:
            print_warning("FILE_UPLOAD_MAX_MEMORY_SIZE non configuré")

        # DATA_UPLOAD_MAX_MEMORY_SIZE
        if hasattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE'):
            size_mb = settings.DATA_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024)
            print_success(f"DATA_UPLOAD_MAX_MEMORY_SIZE = {size_mb:.1f} MB")
        else:
            print_warning("DATA_UPLOAD_MAX_MEMORY_SIZE non configuré")

        # SECRET_KEY
        if settings.SECRET_KEY and len(settings.SECRET_KEY) > 20:
            print_success(f"SECRET_KEY configuré ({len(settings.SECRET_KEY)} caractères)")
        else:
            print_warning("SECRET_KEY trop court ou non configuré")

        return True
    except Exception as e:
        print_error(f"Erreur de vérification des settings : {e}")
        return False

def main():
    print_header("VALIDATION BACKEND DJANGO - SPAS")
    print("Date : 2026-01-22 (J-5 Soutenance)")

    results = []

    # Exécuter les checks
    results.append(("Fichier .env", check_env_file()))
    results.append(("Import Django", check_django_import()))

    # Si Django ne peut pas être importé, arrêter
    if not results[-1][1]:
        print_header("❌ ARRÊT : Django ne peut pas être importé")
        return 1

    results.append(("Configuration Django", check_django_setup()))

    # Si Django ne peut pas être configuré, arrêter
    if not results[-1][1]:
        print_header("❌ ARRÊT : Django ne peut pas être configuré")
        print_warning("Vérifiez votre fichier .env et les variables d'environnement")
        return 1

    results.append(("Modèles Django", check_models()))
    results.append(("Base de données", check_database()))
    results.append(("Permissions RBAC", check_permissions()))
    results.append(("Sécurité Settings", check_settings_security()))

    # Résumé
    print_header("RÉSUMÉ")

    total = len(results)
    passed = sum(1 for _, success in results if success)

    print(f"\n{BOLD}Vérifications : {passed}/{total}{RESET}\n")

    for name, success in results:
        status = f"{GREEN}✅ OK{RESET}" if success else f"{RED}❌ ÉCHEC{RESET}"
        print(f"  {name:30} : {status}")

    score = int((passed / total) * 100)

    print(f"\n{BOLD}Score : {score}/100{RESET}\n")

    if score >= 85:
        print(f"{GREEN}{BOLD}✅ BACKEND PRÊT POUR LA SOUTENANCE !{RESET}")
        return 0
    elif score >= 60:
        print(f"{YELLOW}{BOLD}⚠️  BACKEND PRESQUE PRÊT - Corrigez les erreurs ci-dessus{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}❌ BACKEND NON PRÊT - Action urgente requise{RESET}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  Interrompu par l'utilisateur{RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}❌ Erreur inattendue : {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
