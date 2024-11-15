#rest
from rest_framework import serializers
#models 
from authentication.models import User
#django 
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
#utils 
from authentication.utils import error_message
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
            raise ValidationError(error_message("this email already used","هذا الايميل مستعمل بالفعل"))
        return value
      
      def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        data = super().create(validated_data)
        return data