#!/bin/bash

# JKUAT GPA Calculator - Render Deployment Build Script
# This script automates the setup process for free tier Render deployments
# where interactive shell access is not available

set -e  # Exit immediately if any command fails

echo "=========================================="
echo "JKUAT GPA Calculator - Build Script"
echo "=========================================="

# Pre-flight check: Verify DATABASE_URL is set
echo ""
echo "[0/5] Checking environment configuration..."
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set!"
    echo "   Add DATABASE_URL to Render environment variables"
    echo "   Use Internal Database URL from PostgreSQL resource"
    exit 1
else
    echo "✓ DATABASE_URL is configured"
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: SECRET_KEY is not set!"
    exit 1
else
    echo "✓ SECRET_KEY is configured"
fi

if [ -z "$ALLOWED_HOSTS" ]; then
    echo "⚠ WARNING: ALLOWED_HOSTS not set, using defaults"
else
    echo "✓ ALLOWED_HOSTS is configured"
fi

# Step 1: Install Python Dependencies
echo ""
echo "[1/5] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed successfully"

# Step 2: Collect Static Files
echo ""
echo "[2/5] Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✓ Static files collected successfully"

# Step 3: Run Database Migrations
echo ""
echo "[3/5] Running database migrations..."
python manage.py migrate --noinput
echo "✓ Database migrations completed successfully"

# Step 4: Verify Database Connection
echo ""
echo "[4/5] Verifying database connection..."
python manage.py dbshell << END
SELECT 'Database connection successful!' as status;
\q
END
echo "✓ Database connection verified"

# Step 5: Create Superuser (if credentials provided)
echo ""
echo "[5/5] Checking for superuser credentials..."

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
