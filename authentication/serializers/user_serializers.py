#rest
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
#models 
from authentication.models import User
#django 
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
#utils 
from authentication.utils import message

class RegisterSerializer(serializers.ModelSerializer):
      class Meta:
            model = User
            fields = "__all__"
            extra_kwargs = {
                  "password":{
                        "write_only":True,
                  }
            }

      def validate_email(self, value):
        if User.objects.filter(email=value , is_active=True).exists():
            raise ValidationError(message("this email already used","هذا الايميل مستعمل بالفعل", "error"))
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
              raise ValidationError(message("OTP is invalid", "OTP غير صحيح", "error"))
          user = User.objects.get(email=attrs["email"],otp = attrs["otp"])
          if user.is_otp_expired(): 
              raise ValidationError(message(en = "OTP EXPIRED",ar = "انتهت فعالية الرمز",status="error"))
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
