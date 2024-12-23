import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging
from ..models import Payment

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    print("Webhook received")
    print("Signature Header:", sig_header)
    print("Webhook Secret (length):", len(settings.STRIPE_WEBHOOK_SECRET))
    
    try:
        if isinstance(payload, bytes):
            payload_str = payload.decode('utf-8')
        else:
            payload_str = payload

        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
        
        logger.info(f"Webhook signature verified successfully")
        logger.info(f"Webhook event type: {event.type}")

        if event.type == 'payment_intent.succeeded':
            handle_successful_payment(event.data.object)
        elif event.type == 'payment_intent.payment_failed':
            handle_failed_payment(event.data.object)

        return HttpResponse(status=200)

    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=400)

def handle_successful_payment(payment_intent):
    try:
        payment = Payment.objects.get(payment_intent_id=payment_intent.id)
        payment.status = Payment.PaymentStatus.COMPLETED
        payment.transaction_id = payment_intent.id
        payment.paid = True
        payment.save()
        
        payable = payment.payable
        if payable and hasattr(payable, 'status'):
            if hasattr(payable, 'OrderStatus'):
                payable.status = payable.OrderStatus.PROCESSING
            elif hasattr(payable, 'ServiceStatus'):
                payable.status = payable.ServiceStatus.PROGRESS
            payable.save()
        logger.info(f"Payment {payable.uuid} {payable.status}marked as completed")
        logger.info(f"Payment {payment.uuid} marked as completed")
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for payment_intent: {payment_intent.id}")
        raise

def handle_failed_payment(payment_intent):
    try:
        payment = Payment.objects.get(payment_intent_id=payment_intent.id)
        payment.status = Payment.PaymentStatus.FAILED
        payment.save()
        logger.info(f"Payment {payment.uuid} marked as failed")
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for payment_intent: {payment_intent.id}")
        raise