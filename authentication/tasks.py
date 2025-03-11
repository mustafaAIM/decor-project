from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def send_verification_email_task(email, otp):
    subject = 'Verify your email'
    html_content = render_to_string('authentication/email/verification.html', {
        'otp': otp,
        'valid_minutes': 10
    })
    text_content = strip_tags(html_content)
    
    email_message = EmailMultiAlternatives(
        subject,
        text_content,
        os.getenv("EMAIL_HOST_USER"),
        [email]
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()

@shared_task
def send_reset_password_verification_email_task(email, otp):
    subject = 'Reset Your Password'
    html_content = render_to_string('authentication/email/password_reset.html', {
        'otp': otp,
        'valid_minutes': 10
    })
    text_content = strip_tags(html_content)
    
    email_message = EmailMultiAlternatives(
        subject,
        text_content,
        os.getenv("EMAIL_HOST_USER"),
        [email]
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()