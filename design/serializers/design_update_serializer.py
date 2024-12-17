# rest framework
from rest_framework import serializers
# models
from ..models.desgin_model import Design
from section.models.category_model import Category

class DesignUpdateSerializer(serializers.ModelSerializer):
    category = serializers.UUIDField(required=False)
    
    class Meta:
        model = Design
        fields = ['uuid', 'title', 'description', 'category']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        if 'category' in validated_data:
            category_uuid = validated_data['category']
            category = Category.objects.get(uuid=category_uuid)
            instance.category = category
        instance.save()
        return instance