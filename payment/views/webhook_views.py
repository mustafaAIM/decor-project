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
    print("SIG HEADER",sig_header)

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"Webhook received: {event.type}")

        # Handle the event
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            try:
                payment = Payment.objects.get(payment_intent_id=payment_intent.id)
                payment.status = Payment.PaymentStatus.COMPLETED
                payment.transaction_id = payment_intent.id
                payment.paid = True
                payment.save()
                
                # Update the related order/service status
                payable = payment.payable
                if payable:
                    if hasattr(payable, 'status'):
                        if hasattr(payable, 'OrderStatus'):
                            payable.status = payable.OrderStatus.PROCESSING
                        elif hasattr(payable, 'ServiceStatus'):
                            payable.status = payable.ServiceStatus.IN_PROGRESS
                        payable.save()
                
                logger.info(f"Payment {payment.uuid} marked as completed")
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for payment_intent: {payment_intent.id}")
                return HttpResponse(status=400)

        elif event.type == 'payment_intent.payment_failed':
            payment_intent = event.data.object
            try:
                payment = Payment.objects.get(payment_intent_id=payment_intent.id)
                payment.status = Payment.PaymentStatus.FAILED
                payment.save()
                logger.info(f"Payment {payment.uuid} marked as failed")
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for payment_intent: {payment_intent.id}")
                return HttpResponse(status=400)

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