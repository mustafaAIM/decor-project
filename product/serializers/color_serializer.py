# regular expression
import re
# rest framework
from rest_framework import serializers
# models
from ..models.color_model import Color
# utils
from utils.api_exceptions import BadRequestError

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
            raise BadRequestError(en_message="Invalid hex code.", ar_message="ترميز لوني غير صحيح", status_code=400)
        return value