# rest framework
from rest_framework import serializers
# models
from ..models.rate_model import Rate
from ..models.product_model import Product
from customer.models.customer_model import Customer
# utils
from utils.api_exceptions import BadRequestError, AuthenticationError, NotFoundError

class RateSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField()
    class Meta:
        model = Rate
        exclude = ['customer'] 
        
    def validate(self, data):
        product_instance = Product.objects.filter(uuid=data["product"]).first()
        if not product_instance:
            raise NotFoundError(en_message="Product not found.", ar_message="المنتج غير موجود")
        if not self.context['request'].user:
            raise AuthenticationError(en_message="You Must be logged in to rate products", ar_message="يجب أن تقوم بتسجيل الدخول لتقوم بتفييم المنتجات")
        if not Customer.objects.filter(user=self.context['request'].user).exists():
            raise AuthenticationError(en_message="Only customers can rate products", ar_message="فقط العملاء يمكنهم تقييم المنتجات")
        if Rate.objects.filter(product=product_instance, customer=Customer.objects.get(user=self.context['request'].user)).exists():
            raise BadRequestError(en_message="You have already rated this product.", ar_message="لقد قت بالغعل بتفييم هذا المنتج")
        data["product"] = product_instance
        return data
    
    def create(self, validated_data):
        product_instance = validated_data.pop('product')
        customer = self.context['request'].user.customer
        rate_instance = Rate.objects.create(product=product_instance, customer=customer, **validated_data)
        return rate_instance