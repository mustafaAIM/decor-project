# rest framework
from rest_framework import serializers
# models
from ..models.rate_model import Rate
from ..models.product_model import Product
# utils
from utils.exceptions import BaseCustomException

class RateSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField()
    class Meta:
        model = Rate
        exclude = ['customer'] 
        
    def validate(self, data):
        product_instance = Product.objects.filter(uuid=data["product"]).first()
        if not product_instance:
            raise BaseCustomException(en_message="Product not found.", ar_message="المنتج غير موجود", status_code=404)
        if not self.context['request'].user:
            raise BaseCustomException(en_message="You Must be logged in to rate products", ar_message="يجب أن تقوم بتسجيل الدخول لتقوم بتفييم المنتجات", status_code=401)
        if not self.context['request'].user.cutomer:
            raise BaseCustomException(en_message="Only customers can rate products", ar_message="فقط العملاء يمكنهم تقييم المنتجات", status_code=401)
        if Rate.objects.filter(product=product_instance, customer=self.context['request'].user.customer).exists():
            raise BaseCustomException(en_message="You have already rated this product.", ar_message="لقد قت بالغعل بتفييم هذا المنتج", status_code=400)
        data["product"] = product_instance
        return data
    
    def create(self, validated_data):
        product_instance = validated_data.pop('product')
        customer = self.context['request'].user.customer
        rate_instance = Rate.objects.create(product=product_instance, customer=customer, **validated_data)
        return rate_instance