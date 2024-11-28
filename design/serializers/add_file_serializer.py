from rest_framework import serializers

class AddFileSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    title = serializers.CharField(max_length=255, required=True)
    is_primary = serializers.BooleanField(required=True) 