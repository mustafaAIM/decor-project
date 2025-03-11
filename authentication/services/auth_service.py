#services
from authentication.services.otp_service import OTPService
#models 
from authentication.models import User
#hashers 
from django.contrib.auth.hashers import make_password
#shortcut
from core.utils.shortcuts import get_object_or_404

class AuthenticationService:
    def __init__(self):
        self.model = User.objects
        self.otp_service = OTPService()

    def create_user(self, user_data: dict) -> User:
        user_data['password'] = make_password(user_data['password'])
        user = self.model.create(**user_data)
        self.otp_service.set_strategy('email_verification')
        self.otp_service.send_otp(user.email)
        return user

    def initiate_password_reset(self, email: str) -> None:
        self.otp_service.set_strategy('password_reset')
        self.otp_service.send_otp(email)

    def verify_email(self, email: str, otp: str) -> User:
        user = get_object_or_404(self.model, email=email)
        self.otp_service.set_strategy('email_verification')
        self.otp_service.verify_otp(email, otp)
        user.is_active = True
        self.otp_service.clear_otp(user)
        return user