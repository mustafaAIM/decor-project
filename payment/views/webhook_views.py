import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from ..models import Payment
from order.models import Order
from service.models import ServiceOrder

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        handle_successful_payment(event['data']['object'])
    elif event['type'] == 'payment_intent.payment_failed':
        handle_failed_payment(event['data']['object'])

    return HttpResponse(status=200)

def handle_successful_payment(payment_intent):
    try:
        payment = Payment.objects.get(payment_intent_id=payment_intent.id)
        payment.status = Payment.PaymentStatus.COMPLETED
        payment.transaction_id = payment_intent.charges.data[0].id
        payment.completed_at = timezone.now()
        payment.save()

        # Update order/service status
        payable = payment.payable
        if isinstance(payable, Order):
            payable.status = Order.OrderStatus.PROCESSING
            payable.save()
        elif isinstance(payable, ServiceOrder):
            payable.status = ServiceOrder.ServiceStatus.IN_PROGRESS
            payable.save()

    except Payment.DoesNotExist:
        # Log error or handle missing payment
        pass

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