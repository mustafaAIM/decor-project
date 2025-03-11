from authentication.strategies.otp_strategies import (
    EmailVerificationStrategy,
    PasswordResetStrategy
)
#shortcut
from core.utils.shortcuts import get_object_or_404
#models
from authentication.models import User
#exceptions
from core.exceptions.api import BadRequestException

class OTPService:
    def __init__(self):
        self.model = User
        self._strategies = {
            'email_verification': EmailVerificationStrategy(),
            'password_reset': PasswordResetStrategy(),
        }
        self._strategy = None

    def set_strategy(self, strategy_type: str) -> None:
        if strategy_type not in self._strategies:
            raise BadRequestException(
                en_message=f"Invalid strategy type: {strategy_type}",
                ar_message="نوع استراتيجية غير صالح"
            )
        self._strategy = self._strategies[strategy_type]

    def send_otp(self, email: str) -> None:
        if not self._strategy:
            raise BadRequestException(
                en_message="OTP strategy not set",
                ar_message="لم يتم تحديد استراتيجية OTP"
            )
        
        user = get_object_or_404(self.model, email=email)
        self._strategy.send_otp(user)

    def verify_otp(self, email: str, otp: str) -> bool:
        if not self._strategy:
            raise BadRequestException(
                en_message="OTP strategy not set",
                ar_message="لم يتم تحديد استراتيجية OTP"
            )
        
        user = get_object_or_404(self.model, email=email)
        if not self._strategy.verify_otp(user, otp):
            raise BadRequestException(
                en_message="Invalid or expired OTP",
                ar_message="رمز غير صالح أو منتهي الصلاحية"
            )
        return True

    def clear_otp(self, user) -> None:
        user.otp = None
        user.otp_exp = None
        user.save()

    def resend_otp(self, email: str) -> None:
        if not self._strategy:
            raise BadRequestException(
                en_message="OTP strategy not set",
                ar_message="لم يتم تحديد استراتيجية OTP"
            )
        
        user = get_object_or_404(self.model, email=email)
        if user.is_active:
            raise BadRequestException(
                en_message="User is already verified",
                ar_message="تم التحقق من المستخدم بالفعل"
            )
            
        self._strategy.send_otp(user)
