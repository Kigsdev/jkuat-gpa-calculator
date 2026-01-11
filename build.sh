#!/bin/bash

# JKUAT GPA Calculator - Render Deployment Build Script
# This script automates the setup process for free tier Render deployments
# where interactive shell access is not available

set -e  # Exit immediately if any command fails

echo "=========================================="
echo "JKUAT GPA Calculator - Build Script"
echo "=========================================="

# Step 1: Install Python Dependencies
echo ""
echo "[1/4] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed successfully"

# Step 2: Collect Static Files
echo ""
echo "[2/4] Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✓ Static files collected successfully"

# Step 3: Run Database Migrations
echo ""
echo "[3/4] Running database migrations..."
python manage.py migrate --noinput
echo "✓ Database migrations completed successfully"

# Step 4: Create Superuser (if credentials provided)
echo ""
echo "[4/4] Checking for superuser credentials..."

if [ -z "$DJANGO_SUPERUSER_USERNAME" ] || [ -z "$DJANGO_SUPERUSER_PASSWORD" ] || [ -z "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "⚠ Superuser environment variables not found."
    echo "  To auto-create superuser, set these environment variables on Render:"
    echo "  - DJANGO_SUPERUSER_USERNAME"
    echo "  - DJANGO_SUPERUSER_PASSWORD"
    echo "  - DJANGO_SUPERUSER_EMAIL"
    echo ""
    echo "  Alternatively, register via /accounts/register/ after deployment."
else
    echo "Superuser credentials found. Creating superuser..."
    
    # Use management command for reliable superuser creation
    python manage.py create_admin \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --password "$DJANGO_SUPERUSER_PASSWORD" \
        --email "$DJANGO_SUPERUSER_EMAIL"
fi

echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Application will start on Render's servers"
echo "2. Visit your deployment URL"
echo "3. If superuser created, login at /admin/"
echo "4. If not, register at /accounts/register/"
echo ""
