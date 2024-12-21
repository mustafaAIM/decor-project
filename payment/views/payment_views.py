import stripe
import paypalrestsdk
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from ..models import Payment
from ..serializers.payment_serializers import PaymentSerializer, PaymentIntentSerializer
from order.models import Order
from service.models import ServiceOrder
from utils import BadRequestError
from customer.permissions import IsCustomer

stripe.api_key = settings.STRIPE_SECRET_KEY

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    lookup_field = 'uuid'
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return Payment.objects.filter(
            payable__customer=self.request.user.customer
        )

    def get_platform_urls(self, platform, payment_uuid):
        """Helper method to get platform-specific URLs"""
        if platform == 'web':
            base_url = settings.PAYPAL_WEB_BASE_URL
            return {
                'return_url': f"{base_url}/payment/success/?payment_uuid={payment_uuid}",
                'cancel_url': f"{base_url}/payment/cancel/"
            }
        elif platform == 'ios':
            scheme = settings.PAYPAL_IOS_URL_SCHEME.rstrip('/')
            urls = {
                'return_url': f"{scheme}//payment/success?payment_uuid={payment_uuid}",
                'cancel_url': f"{scheme}//payment/cancel"
            }
            print(urls)
            return urls
        elif platform == 'android':
            scheme = settings.PAYPAL_ANDROID_URL_SCHEME.rstrip('/')
            urls = {
                'return_url': f"{scheme}//payment/success?payment_uuid={payment_uuid}",
                'cancel_url': f"{scheme}//payment/cancel"
            }
            print(urls)
            return urls

    @action(detail=False, methods=['post'], url_path='create-intent')
    def create_payment_intent(self, request):
        serializer = PaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_type = serializer.validated_data['order_type']
        order_uuid = serializer.validated_data['order_uuid']
        payment_method = serializer.validated_data['payment_method']
        platform = serializer.validated_data['platform']

        if order_type == 'order':
            order = get_object_or_404(Order, uuid=order_uuid)
            if order.customer != request.user.customer:
                raise BadRequestError(
                    en_message="You don't have permission to pay for this order",
                    ar_message="ليس لديك صلاحية الدفع لهذا الطلب"
                )
            base_amount = order.total_amount
            content_type = ContentType.objects.get_for_model(Order)
            object_id = order.id
        else:
            service_order = get_object_or_404(ServiceOrder, uuid=order_uuid)
            if service_order.customer != request.user.customer:
                raise BadRequestError(
                    en_message="You don't have permission to pay for this service",
                    ar_message="ليس لديك صلاحية الدفع لهذه الخدمة"
                )
            base_amount = service_order.amount
            content_type = ContentType.objects.get_for_model(ServiceOrder)
            object_id = service_order.id

        amount_details = Payment.calculate_fees(base_amount, payment_method)

        try:
            if payment_method == Payment.PaymentMethod.STRIPE:
                intent = stripe.PaymentIntent.create(
                    amount=int(amount_details['total_amount'] * 100),  
                    currency='usd',
                    metadata={
                        'order_type': order_type,
                        'order_uuid': str(order_uuid),
                        'base_amount': str(amount_details['base_amount']),
                        'fee_amount': str(amount_details['fee_amount'])
                    }
                )

                payment = Payment.objects.create(
                    content_type=content_type,
                    object_id=object_id,
                    amount=amount_details['total_amount'],
                    payment_method=payment_method,
                    payment_intent_id=intent.id
                )

                return Response({
                    'client_secret': intent.client_secret,
                    'payment_uuid': payment.uuid,
                    'amount_details': amount_details,
                    'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
                })

            elif payment_method == Payment.PaymentMethod.PAYPAL:
                payment = Payment.objects.create(
                    content_type=content_type,
                    object_id=object_id,
                    amount=amount_details['total_amount'],
                    payment_method=payment_method,
                )

                platform_urls = self.get_platform_urls(platform, payment.uuid)

                paypal_payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "redirect_urls": {
                        "return_url": platform_urls['return_url'],
                        "cancel_url": platform_urls['cancel_url']
                    },
                    "transactions": [{
                        "amount": {
                            "total": str(amount_details['total_amount']),
                            "currency": "USD",
                            "details": {
                                "subtotal": str(amount_details['base_amount']),
                                "tax": str(amount_details['fee_amount'])
                            }
                        },
                        "description": f"Payment for {'Order' if order_type == 'order' else 'Service'} {order_uuid}"
                    }]
                })
                print(paypal_payment)
                if paypal_payment.create():
                    approval_url = next(link.href for link in paypal_payment.links if link.rel == "approval_url")
                    payment.payment_intent_id = paypal_payment.id
                    payment.save()

                    return Response({
                        'approval_url': approval_url,
                        'payment_uuid': payment.uuid
                    })
                else:
                    print(paypal_payment.error)
                    raise BadRequestError(
                        en_message="Failed to create PayPal payment",
                        ar_message="فشل في إنشاء عملية الدفع عبر باي بال"
                    )

        except (stripe.error.StripeError, paypalrestsdk.ResourceNotFound) as e:
            raise BadRequestError(
                en_message=str(e),
                ar_message="حدث خطأ في معالجة الدفع"
            )

    @action(detail=False, methods=['get'], url_path='paypal-success')
    def paypal_success(self, request):
        payment_uuid = request.query_params.get('payment_uuid')
        payment_id = request.query_params.get('paymentId')
        payer_id = request.query_params.get('PayerID')

        try:
            payment = Payment.objects.get(uuid=payment_uuid)
            paypal_payment = paypalrestsdk.Payment.find(payment_id)

            if paypal_payment.execute({"payer_id": payer_id}):
                payment.status = Payment.PaymentStatus.COMPLETED
                payment.transaction_id = payment_id
                payment.save()

                payable = payment.payable
                if payable is not None:
                    if isinstance(payable, Order):
                        payable.status = Order.OrderStatus.PROCESSING
                    elif isinstance(payable, ServiceOrder):
                        payable.status = ServiceOrder.ServiceStatus.IN_PROGRESS
                    payable.save()
                else:
                    print(f"Warning: No payable found for payment {payment_uuid}")

                return Response({
                    "message": "Payment completed successfully",
                    "payment_uuid": payment_uuid
                })
            else:
                raise BadRequestError(
                    en_message="PayPal payment execution failed",
                    ar_message="فشل في تنفيذ عملية الدفع عبر باي بال"
                )

        except Payment.DoesNotExist:
            raise BadRequestError(
                en_message="Payment not found",
                ar_message="لم يتم العثور على عملية الدفع"
            )
        
        except Exception as e:  
            print(e)
            raise e
