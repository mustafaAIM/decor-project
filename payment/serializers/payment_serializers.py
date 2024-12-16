from rest_framework import serializers
from ..models import Payment
from order.serializers.order_serializers import OrderSerializer
from service.serializers.service_order_serializer import ServiceOrderSerializer

class PaymentSerializer(serializers.ModelSerializer):
    payable_details = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'uuid', 'amount', 'currency', 'payment_method',
            'status', 'transaction_id', 'payment_intent_id',
            'created_at', 'updated_at', 'completed_at',
            'payable_details'
        ]
        read_only_fields = fields

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