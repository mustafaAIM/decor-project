#!/bin/bash

echo "Running migrations..."
python manage.py makemigrations authentication
python manage.py migrate authentication

python manage.py makemigrations employee
python manage.py migrate employee 

python manage.py makemigrations plan
python manage.py migrate plan

python manage.py makemigrations service
python manage.py migrate service

python manage.py makemigrations customer
python manage.py migrate customer

python manage.py makemigrations section
python manage.py migrate section

python manage.py makemigrations product
python manage.py migrate product
 
python manage.py makemigrations cart
python manage.py migrate cart

python manage.py makemigrations complaint
python manage.py migrate complaint

python manage.py makemigrations 
python manage.py migrate 

echo "Collecting static files..."
python manage.py collectstatic --noinput
 
echo "Starting Gunicorn..."
exec gunicorn design_project.wsgi:application --bind 0.0.0.0:8000