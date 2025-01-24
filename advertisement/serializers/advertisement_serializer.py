from rest_framework import serializers
from ..models import Advertisement

class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = [
            'uuid', 
            'title_ar', 
            'title_en', 
            'description_ar', 
            'description_en', 
            'image', 
            'created_at'
        ]
        read_only_fields = ['uuid', 'created_at'] 