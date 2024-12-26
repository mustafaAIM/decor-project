# rest
from rest_framework import serializers
# models
from ..models.supervision_service_model import SupervisionService
from section.models.section_model import Section
# utile
from utils.shortcuts import get_object_or_404

class SupervisionServiceSerializer(serializers.ModelSerializer):
    section = serializers.UUIDField()
    class Meta:
        model = SupervisionService
        fields = [
            'uuid', 
            'title', 'description', 
            'notes',
            'section', 'type',
            'phone_number', 'email', 'address', 'city'
        ]
    
    def create(self, validated_data):
        section_uuid = validated_data.pop('section')
        section = get_object_or_404(Section, uuid=section_uuid)
        customer = self.context['request'].user.customer
        supervisionService = SupervisionService.objects.create(section=section, customer=customer, **validated_data)

        return supervisionService