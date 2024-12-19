# rest framework
from rest_framework import serializers
# models
from ..models.desgin_model import Design
from section.models.category_model import Category
# utile
from utils.shortcuts import get_object_or_404
class DesignUpdateSerializer(serializers.ModelSerializer):
    category = serializers.UUIDField(required=False)
    
    class Meta:
        model = Design
        fields = ['uuid', 'title', 'description', 'category']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        category_uuid = validated_data.pop('category', None)
        if category_uuid:
            category = get_object_or_404(Category, uuid=category_uuid)
        else:
            category = instance.category
        instance.category = category
        
        instance.save()

        return instance