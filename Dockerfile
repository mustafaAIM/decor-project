FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1  

COPY . /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint-django.sh  /entrypoint-django.sh
COPY entrypoint-celery.sh /entrypoint-celery.sh
RUN chmod +x /entrypoint-django.sh 
RUN chmod +x /entrypoint-celery.sh