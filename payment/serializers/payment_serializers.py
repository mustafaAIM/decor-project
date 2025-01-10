from rest_framework import serializers
from ..models import Payment
from order.serializers.order_serializers import OrderSerializer
from service.serializers.service_order_serializer import ServiceOrderSerializer
from decimal import Decimal

class PaymentSerializer(serializers.ModelSerializer):
    payable_details = serializers.SerializerMethodField()
    fee_amount = serializers.SerializerMethodField()
    base_amount = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'uuid', 'amount', 'fee_amount', 'base_amount',
            'currency', 'payment_method', 'status',
            'transaction_id', 'payment_intent_id',
            'created_at', 'updated_at', 'completed_at',
            'payable_details'
        ]
        read_only_fields = fields

    def get_fee_amount(self, obj):
        if obj.payment_method == Payment.PaymentMethod.STRIPE:
            return (obj.amount * Payment.STRIPE_FEE_PERCENTAGE / 100 + Payment.STRIPE_FIXED_FEE).quantize(Decimal('0.01'))
        elif obj.payment_method == Payment.PaymentMethod.PAYPAL:
            return (obj.amount * Payment.PAYPAL_FEE_PERCENTAGE / 100 + Payment.PAYPAL_FIXED_FEE).quantize(Decimal('0.01'))
        return Decimal('0')

    def get_base_amount(self, obj):
        return (obj.amount - self.get_fee_amount(obj)).quantize(Decimal('0.01'))

    def get_payable_details(self, obj):
        if obj.payable:
            if obj.content_type.model == 'order':
                return OrderSerializer(obj.payable).data
            elif obj.content_type.model == 'serviceorder':
                return ServiceOrderSerializer(obj.payable).data
        return None

class PaymentIntentSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=Payment.PaymentMethod.choices)
    order_type = serializers.ChoiceField(choices=['order', 'service_order'])
    order_uuid = serializers.UUIDField()
    platform = serializers.ChoiceField(
        choices=['web', 'ios', 'android'], 
        required=True
    ) 

class RefundSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True) 