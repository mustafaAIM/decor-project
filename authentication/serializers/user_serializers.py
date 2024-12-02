#rest
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
#models 
from authentication.models import User
#django 
from django.contrib.auth.hashers import make_password
from utils import BadRequestError
#utils 
from authentication.utils import message

class RegisterSerializer(serializers.ModelSerializer):
      email = serializers.EmailField(required=True)
      class Meta:
            model = User
            fields = "__all__"
            extra_kwargs = {
                  "password":{
                        "write_only":True,
                  }
            }

      def validate_email(self, value):
        existing_user = User.objects.filter(email=value).first()
        if existing_user:
            if existing_user.is_active:
                raise BadRequestError(
                    en_message="Email is already registered and verified. Please login instead.",
                    ar_message="البريد الإلكتروني مسجل ومفعل بالفعل. الرجاء تسجيل الدخول"
                )
            existing_user.delete()
        return value
      
      def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        data = super().create(validated_data)
        return data
      

class OTPVerificationSerializer(serializers.Serializer):
      email = serializers.EmailField(max_length=255, required=True)
      otp = serializers.CharField(max_length=6)

      def validate(self, attrs):
          
          if not User.objects.filter(email=attrs["email"],otp = attrs["otp"]).exists():
              raise BadRequestError(en_message="OTP is invalid",ar_message="OTP غير صحيح")
          user = User.objects.get(email=attrs["email"],otp = attrs["otp"])
          if user.is_otp_expired(): 
              raise BadRequestError(en_message="OTP EXPIRED",ar_message="انتهت فعالية الرمز")
          user.otp = None
          user.otp_exp = None     
          user.is_active = True
          user.save()   
          return super().validate(attrs)




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role 
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        return data




class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise BadRequestError(en_message="No user is associated with this email address", ar_message="لا يوجد مستخدم مسجل بهذا الايميل")
        return value

class PasswordResetVerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6)
    def validate(self, attrs):
        user = User.objects.filter(email=attrs['email'], otp=attrs['otp']).first()
        if not user:
            raise BadRequestError(en_message="OTP is invalid", ar_message="OTP غير صحيح")
        if user.is_otp_expired():
            raise BadRequestError(en_message="OTP EXPIRED", ar_message="انتهت فعالية الرمز")
        user.otp = None
        user.otp_exp = None
        user.save()
        return attrs

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise BadRequestError(en_message="No user is associated with this email address", ar_message="لا يوجد مستخدم مسجل بهذا الايميل")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.password = make_password(self.validated_data['new_password'])
        user.save()