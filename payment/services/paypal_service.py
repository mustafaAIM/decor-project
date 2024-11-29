import paypalrestsdk
from django.conf import settings
from typing import Dict, Any
from datetime import datetime
from .base import BasePaymentService
from ..models import Payment

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class PayPalService(BasePaymentService):
    def create_payment_intent(self, payment: Payment) -> Dict[str, Any]:
        try:
            paypal_payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": str(payment.amount),
                        "currency": payment.currency
                    },
                    "description": f"Payment for {payment.content_object.__class__.__name__}",
                    "custom": str(payment.uuid)
                }],
                "redirect_urls": {
                    "return_url": settings.PAYPAL_RETURN_URL,
                    "cancel_url": settings.PAYPAL_CANCEL_URL
                }
            })

            if paypal_payment.create():
                payment.provider_payment_id = paypal_payment.id
                payment.save()
                
                approval_url = next(link.href for link in paypal_payment.links 
                                 if link.rel == "approval_url")
                
                return {
                    'payment_id': paypal_payment.id,
                    'approval_url': approval_url
                }
            else:
                payment.status = Payment.PaymentStatus.FAILED
                payment.error_message = paypal_payment.error
                payment.save()
                raise Exception(paypal_payment.error)
                
        except Exception as e:
            payment.status = Payment.PaymentStatus.FAILED
            payment.error_message = str(e)
            payment.save()
            raise

    def execute_payment(self, payment: Payment, payer_id: str) -> bool:
        """Execute a PayPal payment after user approval"""
        try:
            paypal_payment = paypalrestsdk.Payment.find(payment.provider_payment_id)
            if paypal_payment.execute({"payer_id": payer_id}):
                payment.status = Payment.PaymentStatus.COMPLETED
                payment.completed_at = datetime.now()
                payment.save()
                return True
            else:
                payment.status = Payment.PaymentStatus.FAILED
                payment.error_message = paypal_payment.error
                payment.save()
                return False
        except Exception as e:
            payment.status = Payment.PaymentStatus.FAILED
            payment.error_message = str(e)
            payment.save()
            return False

    def process_webhook(self, payload: Dict[str, Any]) -> None:
        """Process PayPal webhook events"""
        event_type = payload.get('event_type')
        resource = payload.get('resource', {})
        
        if event_type == 'PAYMENT.SALE.COMPLETED':
            custom = resource.get('custom')
            try:
                payment = Payment.objects.get(uuid=custom)
                payment.status = Payment.PaymentStatus.COMPLETED
                payment.completed_at = datetime.now()
                payment.save()
            except Payment.DoesNotExist:
                pass
                
        elif event_type == 'PAYMENT.SALE.DENIED':
            custom = resource.get('custom')
            try:
                payment = Payment.objects.get(uuid=custom)
                payment.status = Payment.PaymentStatus.FAILED
                payment.error_message = "Payment denied by PayPal"
                payment.save()
            except Payment.DoesNotExist:
                pass

    def refund_payment(self, payment: Payment) -> bool:
        try:
            paypal_payment = paypalrestsdk.Payment.find(payment.provider_payment_id)
            sale_id = paypal_payment.transactions[0].related_resources[0].sale.id
            
            refund = paypalrestsdk.Sale.find(sale_id).refund({
                "amount": {
                    "total": str(payment.amount),
                    "currency": payment.currency
                }
            })
            
            if refund.success():
                payment.status = Payment.PaymentStatus.REFUNDED
                payment.save()
                return True
            return False
        except Exception:
            return False

    def verify_payment(self, payment: Payment) -> bool:
        try:
            paypal_payment = paypalrestsdk.Payment.find(payment.provider_payment_id)
            return paypal_payment.state == 'approved'
        except Exception:
            return False 