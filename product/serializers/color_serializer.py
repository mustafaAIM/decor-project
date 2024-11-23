# regular expression
import re
# rest framework
from rest_framework import serializers
# models
from ..models.color_model import Color
# 
from ..utils.response import custom_message

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        exclude = ['id']
        extra_kwargs = {
            "hex_code": {
                "required" : True
            }
        }
    def validate_hex_code(self, value):
        if not re.match(r'^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$', value):
            raise serializers.ValidationError(custom_message(en="Invalid hex code.", ar="ترميز لوني غير صحيح", status="error"))
        return value