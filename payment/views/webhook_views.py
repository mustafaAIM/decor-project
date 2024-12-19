import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from ..models import Payment
from order.models import Order
from service.models import ServiceOrder
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        logger.debug(f"Received webhook: {payload.decode('utf-8')}")
        
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"Webhook verified: {event.type}")
        
        if event['type'] == 'payment_intent.succeeded':
            logger.info(f"Processing successful payment: {event['data']['object']['id']}")
            handle_successful_payment(event['data']['object'])
        elif event['type'] == 'payment_intent.payment_failed':
            logger.info(f"Processing failed payment: {event['data']['object']['id']}")
            handle_failed_payment(event['data']['object'])

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=400)

    return HttpResponse(status=200)

def handle_successful_payment(payment_intent):
    try:
        # Simulate database error
        with transaction.atomic():
            payment = Payment.objects.get(payment_intent_id=payment_intent.id)
            logger.info(f"Processing payment: {payment_intent.id}")
            
            # Test various scenarios
            if payment_intent.amount == 1234:  # Test amount
                raise Exception("Simulated error")
                
            payment.status = Payment.PaymentStatus.COMPLETED
            payment.paid = True
            payment.save()
            
    except Payment.DoesNotExist:
        logger.error(f"Payment not found: {payment_intent.id}")
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        # Still return 200 to acknowledge receipt

def handle_failed_payment(payment_intent):
    try:
        payment = Payment.objects.get(payment_intent_id=payment_intent.id)
        payment.status = Payment.PaymentStatus.FAILED
        payment.save()

        # Update order/service status if needed
        payable = payment.payable
        if isinstance(payable, Order):
            payable.status = Order.OrderStatus.PENDING
            payable.save()
        elif isinstance(payable, ServiceOrder):
            payable.status = ServiceOrder.ServiceStatus.PENDING
            payable.save()

    except Payment.DoesNotExist:
        # Log error or handle missing payment
        pass 