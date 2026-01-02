#!/bin/bash
# ============================================
# SPAS - Database Reset Script (Linux/Mac)
# ============================================
# This script completely resets the database
# WARNING: This will DELETE all data!
# Usage: ./scripts/reset_db.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}========================================${NC}"
echo -e "${RED}SPAS Database Reset${NC}"
echo -e "${RED}========================================${NC}"
echo -e "${RED}WARNING: This will DELETE ALL data!${NC}"
echo -e "${RED}========================================${NC}"

# Confirmation prompt
read -p "Are you sure you want to reset the database? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}→${NC} Database reset cancelled"
    exit 0
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓${NC} Environment variables loaded"
else
    echo -e "${RED}✗${NC} .env file not found!"
    exit 1
fi

# Default values
DB_NAME=${DB_NAME:-spas_db}
DB_USER=${DB_USER:-spas_user}
DB_PASSWORD=${DB_PASSWORD:-your_password}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

echo -e "\n${YELLOW}Database Configuration:${NC}"
echo -e "  Name: ${DB_NAME}"
echo -e "  User: ${DB_USER}"
echo -e "  Host: ${DB_HOST}"
echo -e "  Port: ${DB_PORT}"

# Drop existing database
echo -e "\n${YELLOW}Dropping existing database...${NC}"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ${DB_NAME};" 2>/dev/null || true
echo -e "${GREEN}✓${NC} Database dropped"

# Drop existing user
echo -e "\n${YELLOW}Dropping existing user...${NC}"
sudo -u postgres psql -c "DROP USER IF EXISTS ${DB_USER};" 2>/dev/null || true
echo -e "${GREEN}✓${NC} User dropped"

# Remove migration files
echo -e "\n${YELLOW}Removing migration files...${NC}"
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
echo -e "${GREEN}✓${NC} Migration files removed"

# Remove SQLite database if exists (shouldn't be used but just in case)
echo -e "\n${YELLOW}Cleaning up...${NC}"
rm -f db.sqlite3
echo -e "${GREEN}✓${NC} Cleanup completed"

# Reinitialize database
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Reinitializing database...${NC}"
echo -e "${GREEN}========================================${NC}"

# Run init_db.sh
./scripts/init_db.sh

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Database reset completed!${NC}"
echo -e "${GREEN}========================================${NC}"
