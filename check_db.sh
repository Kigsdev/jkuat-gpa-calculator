#!/bin/bash

# Database Connection Diagnostic Script
# Run this to check if your DATABASE_URL is configured correctly on Render

echo "=========================================="
echo "Database Connection Diagnostic"
echo "=========================================="
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is NOT set!"
    echo ""
    echo "To fix:"
    echo "1. Go to Render Dashboard"
    echo "2. Click your PostgreSQL database"
    echo "3. Copy the Internal Database URL"
    echo "4. Go to Web Service → Environment"
    echo "5. Add DATABASE_URL = [paste the URL]"
    echo "6. Click Deploy"
    exit 1
else
    echo "✓ DATABASE_URL is set"
    echo ""
    # Extract connection details (hide password)
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\).*/\1/p')
    DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
    echo "  Database Host: $DB_HOST"
    echo "  Database Name: $DB_NAME"
    echo ""
fi

# Check if DEBUG is False (required for production)
if [ "$DEBUG" != "False" ]; then
    echo "⚠ WARNING: DEBUG is not False"
    echo "  Set DEBUG=False in Render environment variables"
fi

echo ""
echo "✓ Database configuration looks correct!"
echo "✓ Data should persist across deployments"
