import stripe
import paypalrestsdk
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from product.models import ProductColor
from utils import BadRequestError
from utils.notification import notify_admins
from django.utils.translation import gettext as _
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import logging

from ..models import Payment
from ..serializers.payment_serializers import PaymentSerializer, PaymentIntentSerializer, RefundSerializer
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

logger = logging.getLogger(__name__)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    lookup_field = 'uuid'
    permission_classes = [IsCustomer]

    def get_queryset(self):
        """
        Filter payments for orders and services belonging to the current user's customer
        """
        customer = self.request.user.customer
        order_type = ContentType.objects.get_for_model(Order)
        service_type = ContentType.objects.get_for_model(ServiceOrder)
        
        return Payment.objects.filter(
            Q(
                content_type=order_type,
                object_id__in=Order.objects.filter(customer=customer).values('id')
            ) |
            Q(
                content_type=service_type,
                object_id__in=ServiceOrder.objects.filter(customer=customer).values('id')
            )
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

    def validate_order_quantities(self, order):
        """Validate that all items have sufficient quantity"""
        for item in order.items.all():
            product_color = item.product_color
            if product_color.quantity < item.quantity:
                raise BadRequestError(
                    en_message=f"Not enough stock for {product_color.product.name} ({product_color.color.name}). Available: {product_color.quantity}",
                    ar_message=f"الكمية المتوفرة غير كافية {product_color.product.name} ({product_color.color.name}). المتوفر: {product_color.quantity}"
                )

    def decrement_quantities(self, order):
        """Decrement quantities after successful payment"""
        for item in order.items.all():
            product_color = item.product_color
            product_color.quantity -= item.quantity
            product_color.save()

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
            self.validate_order_quantities(order)
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

    @transaction.atomic
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
                payment.paid = True
                payment.completed_at = timezone.now()
                payment.save()

                payable = payment.payable
                if payable is not None:
                    if isinstance(payable, Order):
                        self.decrement_quantities(payable)
                        payable.status = Order.OrderStatus.PROCESSING
                        notify_admins(
                            sender=request.user,
                            message=f"New order payment received: {payable.order_number} - Amount: ${payment.amount}"
                        )
                    elif isinstance(payable, ServiceOrder):
                        payable.status = ServiceOrder.ServiceStatus.PROCESSING
                        notify_admins(
                            sender=request.user,
                            message=f"New service payment received: {payable.service_number} - Amount: ${payment.amount}"
                        )
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

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path='stripe-success')
    def stripe_success(self, request):
        payment_uuid = request.data.get('payment_uuid')
        
        try:
            payment = Payment.objects.get(uuid=payment_uuid)
            if payment.payable.customer != request.user.customer:
                raise BadRequestError(
                    en_message="You don't have permission to complete this payment",
                    ar_message="ليس لديك صلاحية إتمام هذا الدفع"
                )
            
            payment_intent = stripe.PaymentIntent.retrieve(payment.payment_intent_id)
            
            if payment_intent.status == 'succeeded':
                payment.status = Payment.PaymentStatus.COMPLETED
                payment.transaction_id = payment_intent.id
                payment.paid = True
                payment.completed_at = timezone.now()
                payment.save()
                
                payable = payment.payable
                if payable is not None:
                    if isinstance(payable, Order):
                        self.decrement_quantities(payable)
                        payable.status = Order.OrderStatus.PROCESSING
                        notify_admins(
                            sender=request.user,
                            message=f"New order payment received: {payable.order_number} - Amount: ${payment.amount}"
                        )
                    elif isinstance(payable, ServiceOrder):
                        payable.status = ServiceOrder.ServiceStatus.PROCESSING
                        notify_admins(
                            sender=request.user,
                            message=f"New service payment received: {payable.service_number} - Amount: ${payment.amount}"
                        )
                    payable.save()
                
                return Response({
                    "message": "Payment completed successfully",
                    "payment_uuid": payment_uuid,
                    "status": "completed"
                }, status=status.HTTP_200_OK)
            else:
                raise BadRequestError(
                    en_message="Payment has not been completed",
                    ar_message="لم يتم إكمال الدفع"
                )
                
        except Payment.DoesNotExist:
            raise BadRequestError(
                en_message="Payment not found",
                ar_message="لم يتم العثور على عملية الدفع"
            )
        
        except stripe.error.StripeError as e:
            raise BadRequestError(
                en_message=str(e),
                ar_message="حدث خطأ في التحقق من الدفع"
            )

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def refund(self, request, uuid=None):
        payment = self.get_object()
        logger.info(f"Refund request received for payment {payment.uuid}")
        logger.info(f"Payment completed_at: {payment.completed_at}")
        logger.info(f"Current status: {payment.status}")
        logger.info(f"Is paid: {payment.is_paid}")
        
        serializer = RefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Log refund eligibility check
        time_since_completion = None
        if payment.completed_at:
            time_since_completion = timezone.now() - payment.completed_at
            logger.info(f"Time since completion: {time_since_completion}")
        
        if not payment.can_be_refunded:
            logger.warning(f"Refund rejected for payment {payment.uuid}. "
                         f"Status: {payment.status}, "
                         f"Is paid: {payment.is_paid}, "
                         f"Completed at: {payment.completed_at}, "
                         f"Time since completion: {time_since_completion}")
            raise BadRequestError(
                en_message="This payment cannot be refunded. Refunds are only available within 24 hours of payment completion.",
                ar_message="لا يمكن استرداد هذه الدفعة. الاسترداد متاح فقط خلال 24 ساعة من إتمام الدفع."
            )

        try:
            logger.info(f"Processing refund for payment {payment.uuid} via {payment.payment_method}")
            
            if payment.payment_method == Payment.PaymentMethod.STRIPE:
                logger.info(f"Initiating Stripe refund for payment_intent: {payment.payment_intent_id}")
                refund = stripe.Refund.create(
                    payment_intent=payment.payment_intent_id,
                    reason='requested_by_customer'
                )
                refund_id = refund.id
                logger.info(f"Stripe refund created with ID: {refund_id}")
                
            elif payment.payment_method == Payment.PaymentMethod.PAYPAL:
                logger.info(f"Initiating PayPal refund for transaction: {payment.transaction_id}")
                paypal_payment = paypalrestsdk.Payment.find(payment.transaction_id)
                sale_id = paypal_payment.transactions[0].related_resources[0].sale.id
                logger.info(f"Found PayPal sale ID: {sale_id}")
                
                refund = paypalrestsdk.Sale.find(sale_id).refund({
                    "amount": {
                        "total": str(payment.amount),
                        "currency": "USD"
                    }
                })
                
                if not refund.success():
                    logger.error(f"PayPal refund failed: {refund.error}")
                    raise BadRequestError(
                        en_message="PayPal refund failed",
                        ar_message="فشل استرداد المبلغ عبر باي بال"
                    )
                refund_id = refund.id
                logger.info(f"PayPal refund created with ID: {refund_id}")

            # Update payment status
            payment.status = Payment.PaymentStatus.REFUNDED
            payment.refund_id = refund_id
            payment.refund_reason = serializer.validated_data.get('reason', '')
            payment.refunded_at = timezone.now()
            payment.save()
            logger.info(f"Payment {payment.uuid} marked as refunded")

            # Handle payable updates
            payable = payment.payable
            logger.info(f"Processing payable updates for {payable.__class__.__name__} {payable.id}")
            
            if isinstance(payable, Order):
                logger.info(f"Processing order refund for order {payable.order_number}")
                for item in payable.items.all():
                    product_color = item.product_color
                    original_quantity = product_color.quantity
                    product_color.quantity += item.quantity
                    product_color.save()
                    logger.info(f"Updated product {product_color.product.name} quantity from {original_quantity} to {product_color.quantity}")
                payable.status = Order.OrderStatus.REFUNDED
            elif isinstance(payable, ServiceOrder):
                logger.info(f"Processing service order refund for service {payable.service_number}")
                payable.status = ServiceOrder.ServiceStatus.REFUNDED
            
            payable.save()
            logger.info(f"Payable status updated to REFUNDED")

            # Send admin notification
            notify_admins(
                sender=request.user,
                message=f"Refund processed for {payment.payment_method}: {payable.__class__.__name__} {payable.service_number if isinstance(payable, ServiceOrder) else payable.order_number} - Amount: ${payment.amount}"
            )

            return Response({
                'message': _('Refund processed successfully'),
                'refund_id': refund_id
            })

        except (stripe.error.StripeError, paypalrestsdk.ResourceNotFound) as e:
            logger.error(f"Refund failed for payment {payment.uuid}: {str(e)}")
            raise BadRequestError(
                en_message=f"Refund failed: {str(e)}",
                ar_message="فشل استرداد المبلغ"
            )
