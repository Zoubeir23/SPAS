#!/bin/bash
#
# 🚀 Script de Validation Pré-Soutenance SPAS
# ============================================
# Vérifie que l'application est prête pour la démo (J-5)
#
# Usage: bash pre_demo_check.sh
#

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Compteurs
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Fonction pour afficher les headers
print_header() {
    echo ""
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  $1${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Fonction pour checker un élément
check() {
    local description="$1"
    local command="$2"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -n "  [${TOTAL_CHECKS}] ${description}... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ ÉCHEC${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# Fonction pour afficher une info
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Fonction pour afficher un warning
warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Fonction pour afficher un succès
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Fonction pour afficher une erreur
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
clear
echo -e "${BOLD}${BLUE}"
cat << "EOF"
  ____  ____   _    ____    ____            ____
 / ___||  _ \ / \  / ___|  |  _ \ _ __ ___  |  _ \  ___ _ __ ___   ___
 \___ \| |_) / _ \ \___ \  | |_) | '__/ _ \ | | | |/ _ \ '_ ` _ \ / _ \
  ___) |  __/ ___ \ ___) | |  __/| | |  __/ | |_| |  __/ | | | | | (_) |
 |____/|_| /_/   \_\____/  |_|   |_|  \___| |____/ \___|_| |_| |_|\___/

         Système de Validation Pré-Soutenance (J-5)
EOF
echo -e "${NC}"

print_header "1️⃣  VÉRIFICATION DE L'ENVIRONNEMENT"

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    success "Python installé : version ${PYTHON_VERSION}"

    # Vérifier que c'est Python 3.10+
    if [[ $(echo "$PYTHON_VERSION" | cut -d. -f1,2 | tr -d '.') -ge 310 ]]; then
        success "Version Python compatible (>= 3.10)"
    else
        warn "Version Python ${PYTHON_VERSION} détectée. Recommandé: 3.10+"
    fi
else
    error "Python 3 non installé !"
fi

# Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    success "Node.js installé : ${NODE_VERSION}"
else
    warn "Node.js non installé (optionnel pour backend seul)"
fi

# Git
if command -v git &> /dev/null; then
    GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "N/A")
    success "Git installé - Branche actuelle : ${GIT_BRANCH}"
else
    warn "Git non installé"
fi

print_header "2️⃣  VÉRIFICATION DES FICHIERS CRITIQUES"

# Backend files
check "backend/manage.py existe" "test -f backend/manage.py"
check "backend/requirements.txt existe" "test -f backend/requirements.txt"
check "backend/config/settings.py existe" "test -f backend/config/settings.py"
check "backend/.env.example existe" "test -f backend/.env.example"

# Frontend files (optionnel)
if [ -d "frontend" ]; then
    info "Frontend détecté"
    check "frontend/package.json existe" "test -f frontend/package.json"
    check "frontend/src existe" "test -d frontend/src"
fi

# Documentation
check "SECURITY.md existe" "test -f SECURITY.md"
check "AUDIT_FINAL_CORRECTIONS.md existe" "test -f AUDIT_FINAL_CORRECTIONS.md"

print_header "3️⃣  VÉRIFICATION DES CORRECTIFS DE SÉCURITÉ"

info "Exécution du script de validation des correctifs..."
if [ -f "validate_security_fixes.py" ]; then
    python3 validate_security_fixes.py
    if [ $? -eq 0 ]; then
        success "Tous les correctifs de sécurité sont appliqués !"
        PASSED_CHECKS=$((PASSED_CHECKS + 3))
        TOTAL_CHECKS=$((TOTAL_CHECKS + 3))
    else
        error "Certains correctifs manquent !"
        FAILED_CHECKS=$((FAILED_CHECKS + 3))
        TOTAL_CHECKS=$((TOTAL_CHECKS + 3))
    fi
else
    warn "Script validate_security_fixes.py non trouvé"
fi

print_header "4️⃣  VÉRIFICATION DE LA STRUCTURE DU PROJET"

# Backend apps
info "Vérification des applications Django..."
for app in users students programs sessions grades predictions ml alerts interventions core authentication; do
    if [ -d "backend/apps/$app" ]; then
        success "App '$app' détectée"
    else
        warn "App '$app' manquante (peut être optionnelle)"
    fi
done

print_header "5️⃣  VÉRIFICATION GIT & COMMITS"

# Git status
if [ -d ".git" ]; then
    UNCOMMITTED=$(git status --porcelain | wc -l)
    if [ "$UNCOMMITTED" -eq 0 ]; then
        success "Aucun changement non commité"
    else
        warn "${UNCOMMITTED} fichier(s) non commité(s)"
        git status --short | head -5
    fi

    # Dernier commit
    LAST_COMMIT=$(git log -1 --oneline 2>/dev/null)
    info "Dernier commit : ${LAST_COMMIT}"

    # Commits récents avec "fix" ou "security"
    SECURITY_COMMITS=$(git log --oneline --all --grep="security\|fix" -i | head -3)
    if [ ! -z "$SECURITY_COMMITS" ]; then
        echo ""
        info "Commits de sécurité récents :"
        echo "$SECURITY_COMMITS" | while read line; do
            echo "    📝 $line"
        done
    fi
else
    warn "Pas de dépôt Git détecté"
fi

print_header "6️⃣  CHECKLIST PRÉ-SOUTENANCE"

echo -e "\n${BOLD}Points à vérifier MANUELLEMENT avant la démo :${NC}\n"

echo "  Backend :"
echo "    [ ] Créer un fichier .env depuis .env.example"
echo "    [ ] Configurer DATABASE_URL (PostgreSQL ou SQLite)"
echo "    [ ] Configurer SECRET_KEY"
echo "    [ ] Lancer : python manage.py migrate"
echo "    [ ] Lancer : python manage.py seed_isi_data"
echo "    [ ] Créer un superuser admin"
echo "    [ ] Tester : python manage.py runserver"
echo ""
echo "  Frontend (si utilisé) :"
echo "    [ ] Lancer : npm install"
echo "    [ ] Vérifier .env pour VITE_API_URL"
echo "    [ ] Tester : npm run dev"
echo ""
echo "  Celery (tâches ML) :"
echo "    [ ] Redis installé et lancé"
echo "    [ ] Tester : celery -A config worker -l info"
echo ""
echo "  Comptes de Démo :"
echo "    [ ] Admin : email/password testés"
echo "    [ ] Teacher : email/password testés"
echo "    [ ] Fichier CSV de test (< 5MB) prêt"
echo ""
echo "  Données :"
echo "    [ ] Au moins 1 département seedé"
echo "    [ ] Au moins 3 filières seedées"
echo "    [ ] Au moins 1 modèle ML entraîné"
echo ""

print_header "📊  RÉSUMÉ DES VÉRIFICATIONS"

echo -e "\n  ${BOLD}Total de vérifications : ${TOTAL_CHECKS}${NC}"
echo -e "  ${GREEN}✅ Réussies : ${PASSED_CHECKS}${NC}"
echo -e "  ${RED}❌ Échouées : ${FAILED_CHECKS}${NC}"

SCORE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
echo ""
echo -e "  ${BOLD}Score de préparation : ${SCORE}/100${NC}"

echo ""
if [ $SCORE -ge 75 ]; then
    echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║                                                               ║${NC}"
    echo -e "${GREEN}${BOLD}║   ✅ PRÊT POUR LA SOUTENANCE !                                ║${NC}"
    echo -e "${GREEN}${BOLD}║                                                               ║${NC}"
    echo -e "${GREEN}${BOLD}║   Les correctifs de sécurité sont appliqués.                 ║${NC}"
    echo -e "${GREEN}${BOLD}║   Complète la checklist manuelle ci-dessus.                  ║${NC}"
    echo -e "${GREEN}${BOLD}║                                                               ║${NC}"
    echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════════╝${NC}"
elif [ $SCORE -ge 50 ]; then
    echo -e "${YELLOW}${BOLD}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}${BOLD}║                                                               ║${NC}"
    echo -e "${YELLOW}${BOLD}║   ⚠️  PRÉPARATION MOYENNE                                     ║${NC}"
    echo -e "${YELLOW}${BOLD}║                                                               ║${NC}"
    echo -e "${YELLOW}${BOLD}║   Corrige les erreurs ci-dessus avant la soutenance.         ║${NC}"
    echo -e "${YELLOW}${BOLD}║                                                               ║${NC}"
    echo -e "${YELLOW}${BOLD}╚═══════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}${BOLD}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}${BOLD}║                                                               ║${NC}"
    echo -e "${RED}${BOLD}║   ❌ NON PRÊT POUR LA SOUTENANCE                              ║${NC}"
    echo -e "${RED}${BOLD}║                                                               ║${NC}"
    echo -e "${RED}${BOLD}║   Action URGENTE requise. Corrige les erreurs critiques.     ║${NC}"
    echo -e "${RED}${BOLD}║                                                               ║${NC}"
    echo -e "${RED}${BOLD}╚═══════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo -e "${BOLD}💡 Prochaine étape :${NC} Complète la checklist manuelle ci-dessus"
echo -e "${BOLD}📖 Documentation :${NC} Consulte AUDIT_FINAL_CORRECTIONS.md pour les détails"
echo ""

exit 0
