from abc import ABC, abstractmethod
from django.utils import timezone
from authentication.tasks import (
    send_verification_email_task,
    send_reset_password_verification_email_task
)
from authentication.utils import generate_random_otp
from authentication.models import User

class OTPStrategy(ABC):
    @abstractmethod
    def send_otp(self, user) -> None:
        pass

    @abstractmethod
    def verify_otp(self, user, otp: str) -> bool:
        pass
    
    @staticmethod
    def generate_otp(user):
        otp = generate_random_otp()
        user.otp = otp
        user.otp_exp = timezone.now()
        user.save()
        data = tuple([otp, user.email])
        return data

class EmailVerificationStrategy(OTPStrategy):
    def send_otp(self, user) -> None:
        otp, email = super().generate_otp(user)
        send_verification_email_task.delay(email, otp)

    def verify_otp(self, user:User, otp: str) -> bool:
        return user.otp == otp and not user.is_otp_expired()

class PasswordResetStrategy(OTPStrategy):
    def send_otp(self, user) -> None:
        otp, email = super().generate_otp(user)
        send_reset_password_verification_email_task.delay(email, otp)

    def verify_otp(self, user, otp: str) -> bool:
        return user.otp == otp and not user.is_otp_expired()
