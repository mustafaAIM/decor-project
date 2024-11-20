# rest framework
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
# models
from ..models.rate_model import Rate
from ..models.product_model import Product
# utils
from ..utils.response import custom_message

class RateSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField()
    class Meta:
        model = Rate
        exclude = ['user'] 
        
    def validate(self, data):
        product_instance = Product.objects.filter(uuid=data["product"]).first()
        if not product_instance:
            raise ValidationError(custom_message(en="Product not found.", ar="المنتج غير موجود", status="error"))
        if Rate.objects.filter(product=product_instance, user=self.context['request'].user).exists():
            raise ValidationError(custom_message(en="You have already rated this product.", ar="لقد قت بالغعل بتفييم هذا المنتج", status="error"))
        data["product"] = product_instance
        return data
    
    def create(self, validated_data):
        product_instance = validated_data.pop('product')
        user = self.context['request'].user 
        rate_instance = Rate.objects.create(product=product_instance, user=user, **validated_data)
        return rate_instance