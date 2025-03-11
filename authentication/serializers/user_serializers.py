#rest
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
#models 
from authentication.models import User
#django 
from core.exceptions.api import BadRequestException
#utils 
from authentication.services.auth_service import AuthenticationService
from authentication.services.password_service import PasswordService
from authentication.services.profile_service import ProfileService
#validator
from authentication.validators import PasswordPolicyValidator
class RegisterSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=..., **kwargs):
        self.password_validator = PasswordPolicyValidator()
        super().__init__(instance, data, **kwargs)

    email = serializers.EmailField(required=True)
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_password(self,value):
        self.password_validator.validate(value)
        return value
    
    def validate_email(self, value):
        existing_user = User.objects.with_deleted().filter(email=value).first()
        if existing_user:
            if existing_user.is_active:
                raise BadRequestException(
                    en_message="Email is already registered and verified. Please login instead.",
                    ar_message="البريد الإلكتروني مسجل ومفعل بالفعل. الرجاء تسجيل الدخول"
                )
            existing_user.hard_delete()
        return value

    def create(self, validated_data):
        validated_data.pop("groups", None)
        validated_data.pop("user_permissions", None)
        return AuthenticationService().create_user(validated_data)

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        AuthenticationService().verify_email(attrs["email"], attrs["otp"])
        return super().validate(attrs)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_service = PasswordService()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise BadRequestException(
                en_message="No user is associated with this email address",
                ar_message="لا يوجد مستخدم مسجل بهذا الايميل"
            )
        self.password_service.request_reset(value)
        return value


class PasswordResetVerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_service = PasswordService()

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        self.password_service.verify_reset_otp(
            validated_data['email'],
            validated_data['otp']
        )
        return validated_data

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_service = PasswordService()

    def save(self):
        self.password_service.reset_password(
            self.validated_data['email'],
            self.validated_data['new_password']
        )

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role 
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user_serializer = UserLoginSerializer(self.user)
        data['user'] = user_serializer.data
        data['role'] = self.user.role
        return data

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uuid', 'email', 'first_name', 'last_name', 'phone', 'address', 'role', 'image')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'uuid',
            'email',
            'first_name',
            'last_name',
            'phone',
            'address',
            'image'
        )
        read_only_fields = ('uuid', 'email')

    def update(self, instance, validated_data):
        return ProfileService().update_profile(instance, validated_data)