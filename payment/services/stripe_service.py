import stripe
from django.conf import settings
from typing import Dict, Any
from datetime import datetime
from .base import BasePaymentService
from ..models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService(BasePaymentService):
    def create_payment_intent(self, payment: Payment) -> Dict[str, Any]:
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),
                currency=payment.currency.lower(),
                metadata={
                    'payment_uuid': str(payment.uuid),
                    'user_id': str(payment.user.id),
                },
                description=f"Payment for {payment.content_object.__class__.__name__}"
            )
            
            payment.provider_payment_intent = intent.id
            payment.save()
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
        except stripe.error.StripeError as e:
            payment.status = Payment.PaymentStatus.FAILED
            payment.error_message = str(e)
            payment.save()
            raise

    def process_webhook(self, payload: Dict[str, Any]) -> None:
        event = stripe.Event.construct_from(payload, stripe.api_key)
        
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            payment = Payment.objects.get(
                provider_payment_intent=payment_intent.id
            )
            payment.status = Payment.PaymentStatus.COMPLETED
            payment.completed_at = datetime.now()
            payment.save()
            
        elif event.type == 'payment_intent.payment_failed':
            payment_intent = event.data.object
            payment = Payment.objects.get(
                provider_payment_intent=payment_intent.id
            )
            payment.status = Payment.PaymentStatus.FAILED
            payment.error_message = payment_intent.last_payment_error
            payment.save()

    def refund_payment(self, payment: Payment) -> bool:
        try:
            refund = stripe.Refund.create(
                payment_intent=payment.provider_payment_intent
            )
            if refund.status == 'succeeded':
                payment.status = Payment.PaymentStatus.REFUNDED
                payment.save()
                return True
            return False
        except stripe.error.StripeError:
            return False

    def verify_payment(self, payment: Payment) -> bool:
        try:
            intent = stripe.PaymentIntent.retrieve(
                payment.provider_payment_intent
            )
            return intent.status == 'succeeded'
        except stripe.error.StripeError:
            return False