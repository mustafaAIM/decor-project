from rest_framework import serializers
from section.models import Category
from utils.api_exceptions import BadRequestError
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['uuid', 'section', 'title', 'description', 'image']
        read_only_fields = ['uuid']

    def validate(self, data):
        title = data.get('title')
        section = data.get('section')

        if self.instance: 
            exists = Category.objects.filter(
                title__iexact=title,
                section=section
            ).exclude(pk=self.instance.pk).exists()
        else:  
            exists = Category.objects.filter(
                title__iexact=title,
                section=section
            ).exists()
            
        if exists:
            raise BadRequestError(en_message="A category with this title already exists in this section.",ar_message="هناك فئة بهذا الاسم بالفعل في هذا القسم")
        return data