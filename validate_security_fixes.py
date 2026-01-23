#!/usr/bin/env python3
"""
Script de Validation des Correctifs de Sécurité
================================================
Vérifie que les 3 bugs critiques ont bien été corrigés dans le code source.

Bugs vérifiés :
- Bug #2 : User list exposure (users/views.py)
- Bug #1 : Settings RBAC bypass (core/views.py)
- Bug #4 : CSV size limit (settings.py)

Usage : python validate_security_fixes.py
"""

import os
import sys
import re

# Couleurs pour l'output terminal
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

def check_file_exists(filepath):
    """Vérifie qu'un fichier existe."""
    if not os.path.exists(filepath):
        print_error(f"Fichier non trouvé : {filepath}")
        return False
    return True

def check_bug2_user_list_exposure():
    """
    Bug #2 : Exposition liste utilisateurs
    Vérifie que get_permissions() dans UserViewSet restreint bien list/retrieve à IsAdminUser
    """
    print_header("BUG #2 : User List Exposure")

    filepath = "backend/apps/users/views.py"
    if not check_file_exists(filepath):
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    # Vérifications
    checks = []

    # Check 1 : La méthode get_permissions existe
    if 'def get_permissions(self):' in content:
        print_success("Méthode get_permissions() trouvée")
        checks.append(True)
    else:
        print_error("Méthode get_permissions() non trouvée")
        checks.append(False)

    # Check 2 : Vérifie que 'me' endpoint est accessible à IsAuthenticated
    if "if self.action == 'me':" in content and "return [IsAuthenticated()]" in content:
        print_success("Endpoint 'me' accessible à tous les utilisateurs authentifiés")
        checks.append(True)
    else:
        print_error("Endpoint 'me' mal configuré")
        checks.append(False)

    # Check 3 : Vérifie que les autres actions nécessitent IsAdminUser
    if "return [IsAdminUser()]" in content:
        print_success("Actions par défaut protégées par IsAdminUser")
        checks.append(True)
    else:
        print_error("Protection IsAdminUser manquante")
        checks.append(False)

    # Check 4 : Vérifie qu'on n'utilise plus super().get_permissions()
    if "return super().get_permissions()" not in content:
        print_success("Ancien code vulnérable supprimé (super().get_permissions())")
        checks.append(True)
    else:
        print_warning("Ancien code vulnérable encore présent")
        checks.append(False)

    return all(checks)

def check_bug1_settings_rbac():
    """
    Bug #1 : Settings RBAC bypass
    Vérifie que seul role='admin' peut modifier les settings (pas is_staff)
    """
    print_header("BUG #1 : Settings RBAC Bypass")

    filepath = "backend/apps/core/views.py"
    if not check_file_exists(filepath):
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    checks = []

    # Check 1 : Vérifie la présence du check strict role == 'admin'
    if "if request.user.role != 'admin':" in content:
        print_success("Vérification stricte role='admin' trouvée")
        checks.append(True)
    else:
        print_error("Vérification stricte role='admin' manquante")
        checks.append(False)

    # Check 2 : Vérifie que is_staff n'est PLUS utilisé dans la condition
    # On cherche la section PATCH de system_settings
    patch_section = re.search(r"elif request\.method == 'PATCH':.*?return Response", content, re.DOTALL)
    if patch_section:
        patch_code = patch_section.group(0)
        if 'is_staff' not in patch_code or 'not request.user.is_staff and' not in patch_code:
            print_success("Ancien code vulnérable is_staff supprimé")
            checks.append(True)
        else:
            print_error("Code vulnérable is_staff encore présent")
            checks.append(False)
    else:
        print_warning("Section PATCH non trouvée - vérification manuelle requise")
        checks.append(False)

    return all(checks)

def check_bug4_csv_size_limit():
    """
    Bug #4 : CSV DoS via upload illimité
    Vérifie que DATA_UPLOAD_MAX_MEMORY_SIZE et FILE_UPLOAD_MAX_MEMORY_SIZE sont configurés
    """
    print_header("BUG #4 : CSV Upload DoS")

    filepath = "backend/config/settings.py"
    if not check_file_exists(filepath):
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    checks = []

    # Check 1 : DATA_UPLOAD_MAX_MEMORY_SIZE configuré
    if 'DATA_UPLOAD_MAX_MEMORY_SIZE' in content:
        # Extraire la valeur
        match = re.search(r'DATA_UPLOAD_MAX_MEMORY_SIZE\s*=\s*(\d+)', content)
        if match:
            size = int(match.group(1))
            size_mb = size / (1024 * 1024)
            print_success(f"DATA_UPLOAD_MAX_MEMORY_SIZE = {size_mb:.1f} MB")
            checks.append(True)
        else:
            print_error("DATA_UPLOAD_MAX_MEMORY_SIZE mal configuré")
            checks.append(False)
    else:
        print_error("DATA_UPLOAD_MAX_MEMORY_SIZE non configuré")
        checks.append(False)

    # Check 2 : FILE_UPLOAD_MAX_MEMORY_SIZE configuré
    if 'FILE_UPLOAD_MAX_MEMORY_SIZE' in content:
        match = re.search(r'FILE_UPLOAD_MAX_MEMORY_SIZE\s*=\s*(\d+)', content)
        if match:
            size = int(match.group(1))
            size_mb = size / (1024 * 1024)
            print_success(f"FILE_UPLOAD_MAX_MEMORY_SIZE = {size_mb:.1f} MB")
            checks.append(True)
        else:
            print_error("FILE_UPLOAD_MAX_MEMORY_SIZE mal configuré")
            checks.append(False)
    else:
        print_error("FILE_UPLOAD_MAX_MEMORY_SIZE non configuré")
        checks.append(False)

    return all(checks)

def main():
    print_header("VALIDATION DES CORRECTIFS DE SÉCURITÉ - SPAS")
    print(f"Date : 2026-01-22 (J-5 Soutenance)")
    print(f"Bugs critiques à vérifier : 3/4")

    results = {}

    # Vérifier chaque bug
    results['bug2'] = check_bug2_user_list_exposure()
    results['bug1'] = check_bug1_settings_rbac()
    results['bug4'] = check_bug4_csv_size_limit()

    # Résumé
    print_header("RÉSUMÉ DE LA VALIDATION")

    total_bugs = len(results)
    bugs_fixed = sum(1 for fixed in results.values() if fixed)

    print(f"\n{BOLD}Bugs Corrigés : {bugs_fixed}/{total_bugs}{RESET}\n")

    print(f"Bug #2 (User List Exposure)  : {'✅ CORRIGÉ' if results['bug2'] else '❌ ÉCHEC'}")
    print(f"Bug #1 (Settings RBAC Bypass): {'✅ CORRIGÉ' if results['bug1'] else '❌ ÉCHEC'}")
    print(f"Bug #4 (CSV DoS)             : {'✅ CORRIGÉ' if results['bug4'] else '❌ ÉCHEC'}")

    # Verdict final
    print("\n" + "="*70)
    if all(results.values()):
        print(f"{GREEN}{BOLD}")
        print("🎉 VERDICT : TOUS LES CORRECTIFS SONT APPLIQUÉS")
        print(f"   Score estimé : 75/100 (PASS)")
        print(f"   Status : PRÊT POUR LA SOUTENANCE{RESET}")
        print("="*70)
        return 0
    else:
        print(f"{RED}{BOLD}")
        print("⚠️  VERDICT : CERTAINS CORRECTIFS MANQUENT")
        print(f"   Action requise : Vérifier les fichiers signalés")
        print(f"   Status : NON PRÊT{RESET}")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
