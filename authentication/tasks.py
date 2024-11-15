from celery import shared_task
from django.core.mail import send_mail
import os
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def send_verification_email_task(email, otp):
    send_mail(
        'Verify your email',
        f'Please verify your email: {otp}',
        os.getenv("EMAIL_HOST_USER"),
        [email],
        fail_silently=False,
    )