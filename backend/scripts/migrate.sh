#!/bin/bash
# ============================================
# SPAS - Complete Migration Script (Linux/Mac)
# ============================================
# This script handles all migration tasks for SPAS
# Usage: ./scripts/migrate.sh [--fresh]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}SPAS Migration Script${NC}"
echo -e "${BLUE}========================================${NC}"

# Change to project directory
cd "$PROJECT_DIR"

# Check if fresh migration is requested
FRESH_MIGRATION=false
if [ "$1" == "--fresh" ]; then
    FRESH_MIGRATION=true
    echo -e "${YELLOW}→ Fresh migration requested${NC}"
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓${NC} Environment variables loaded"
else
    echo -e "${RED}✗${NC} .env file not found!"
    echo -e "${YELLOW}→${NC} Copy .env.example to .env and configure it"
    exit 1
fi

# Check migration dependencies
echo -e "\n${YELLOW}Checking migration dependencies...${NC}"

# Check if apps have __init__.py files
for app in apps/*/; do
    if [ ! -f "${app}__init__.py" ]; then
        echo -e "${YELLOW}→${NC} Creating __init__.py for ${app}"
        touch "${app}__init__.py"
    fi
done

# Create migrations directories if they don't exist
for app in apps/*/; do
    migrations_dir="${app}migrations"
    if [ ! -d "$migrations_dir" ]; then
        echo -e "${YELLOW}→${NC} Creating migrations directory for ${app}"
        mkdir -p "$migrations_dir"
        touch "${migrations_dir}/__init__.py"
    fi
done

echo -e "${GREEN}✓${NC} Migration dependencies checked"

# Delete old migrations if fresh migration
if [ "$FRESH_MIGRATION" == true ]; then
    echo -e "\n${YELLOW}Removing old migrations...${NC}"
    for app in apps/*/migrations/; do
        if [ -d "$app" ]; then
            find "$app" -type f -name "*.py" ! -name "__init__.py" -delete
            echo -e "${GREEN}✓${NC} Removed migrations from ${app}"
        fi
    done
fi

# Check for migration conflicts
echo -e "\n${YELLOW}Checking for migration conflicts...${NC}"
python manage.py makemigrations --check --dry-run || {
    echo -e "${YELLOW}→${NC} There are changes that need migrations"
}

# Create migrations for each app in dependency order
echo -e "\n${YELLOW}Creating migrations...${NC}"

# Order matters - dependencies first!
APPS_ORDER=(
    "users"
    "programs"
    "sessions"
    "students"
    "grades"
    "attendance"
    "ml"
    "predictions"
    "alerts"
)

for app in "${APPS_ORDER[@]}"; do
    echo -e "${YELLOW}→${NC} Creating migrations for apps.${app}..."
    python manage.py makemigrations "$app" --noinput || {
        echo -e "${YELLOW}→${NC} No changes detected for apps.${app}"
    }
done

# Create any remaining migrations
echo -e "\n${YELLOW}Creating remaining migrations...${NC}"
python manage.py makemigrations --noinput

# Show migration plan
echo -e "\n${YELLOW}Migration plan:${NC}"
python manage.py showmigrations

# Apply migrations
echo -e "\n${YELLOW}Applying migrations...${NC}"
python manage.py migrate --noinput

# Verify migrations
echo -e "\n${YELLOW}Verifying migrations...${NC}"
python manage.py showmigrations

# Create cache tables if using database cache
if grep -q "django.core.cache.backends.db" config/settings.py; then
    echo -e "\n${YELLOW}Creating cache tables...${NC}"
    python manage.py createcachetable || echo -e "${YELLOW}→${NC} Cache table already exists"
fi

# Collect static files (if not in development)
if [ "${DEBUG}" != "True" ]; then
    echo -e "\n${YELLOW}Collecting static files...${NC}"
    python manage.py collectstatic --noinput
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Migrations completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${YELLOW}Migration summary:${NC}"
python manage.py showmigrations | grep -E "^\[X\]" | wc -l | xargs echo "  Applied migrations:"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Create superuser: python manage.py createsuperuser"
echo -e "  2. Load initial data: python manage.py loaddata fixtures/*.json"
echo -e "  3. Start development server: python manage.py runserver"
echo ""
