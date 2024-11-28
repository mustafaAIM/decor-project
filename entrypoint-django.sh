#!/bin/bash

echo "Starting Django deployment..."

# Function to run migrations for an app
run_migrations() {
    app_name=$1
    echo "Running migrations for $app_name..."
    python manage.py makemigrations $app_name --noinput || exit 1
    python manage.py migrate $app_name --noinput || exit 1
}

# Function to check if migrations are needed
check_migrations() {
    python manage.py showmigrations | grep -q "\[ \]"
    return $?
}

echo "Checking database connection..."
python << END
import sys
import time
import psycopg2
from django.db import connections
from django.db.utils import OperationalError

start_time = time.time()
while True:
    try:
        connections['default'].ensure_connection()
        break
    except OperationalError:
        if time.time() - start_time > 30:
            print("Could not connect to database after 30 seconds")
            sys.exit(1)
        time.sleep(1)
END

# Clear any pending migrations first
echo "Checking for conflicting migrations..."
python manage.py migrate --fake-initial

# Run migrations in dependency order
echo "Running migrations in order..."

# Base apps (no dependencies)
run_migrations "authentication"  # User model needs to be first
run_migrations "file_management"

# Apps that depend on authentication
run_migrations "employee"
run_migrations "customer"
run_migrations "admin"

# Feature apps
run_migrations "section"  # Categories need to exist before products
run_migrations "product"
run_migrations "service"
run_migrations "plan"
run_migrations "design"
run_migrations "cart"
run_migrations "complaint"

# Final migration check
echo "Running any remaining migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Verify all migrations are applied
if check_migrations; then
    echo "Some migrations are not applied. Please check the migration status."
    python manage.py showmigrations
    exit 1
fi

echo "Creating cache tables..."
python manage.py createcachetable --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Optional: Run data seeding if needed
if [ "$DJANGO_SETTINGS_MODULE" = "design_project.settings.dev" ]; then
    echo "Development environment detected, seeding initial data..."
    python manage.py seed_products
fi

echo "Starting Gunicorn..."
exec gunicorn design_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info