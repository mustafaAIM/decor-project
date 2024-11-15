#!/bin/bash

echo "Running migrations..."
python manage.py makemigrations authentication
python manage.py migrate authentication

python manage.py makemigrations 
python manage.py migrate
 
echo "Collecting static files..."
python manage.py collectstatic --noinput
 
echo "Starting Gunicorn..."
exec gunicorn design_project.wsgi:application --bind 0.0.0.0:8000
