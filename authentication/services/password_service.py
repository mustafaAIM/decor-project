from django.utils import timezone
#models
from authentication.models import User
from django.contrib.auth.hashers import make_password
#services
from authentication.services.otp_service import OTPService
#exceptions
from core.exceptions.api import BadRequestException
#utils
from authentication.utils import generate_random_otp
#tasks
from authentication.tasks import send_reset_password_verification_email_task

class PasswordService:
    def __init__(self):
        self.model = User.objects
        self.otp_service = OTPService()
        self.otp_service.set_strategy("password_reset")

    def request_reset(self, email: str) -> None:
        self.otp_service.send_otp(email)
        
    def verify_reset_otp(self, email: str, otp: str) -> None:
        if not self.otp_service.verify_otp(email, otp):
            raise BadRequestException(
                en_message="Invalid or expired OTP",
                ar_message="رمز غير صالح أو منتهي الصلاحية"
            )
        user = self.model.get(email=email)
        self.otp_service.clear_otp(user)

    def reset_password(self, email: str, new_password: str) -> None:
        user = self.model.get(email=email)
        user.password = make_password(new_password)
        user.save()