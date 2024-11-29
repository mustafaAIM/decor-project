from typing import Optional
from django.conf import settings
from .base import BasePaymentService
from .stripe_service import StripeService
from .paypal_service import PayPalService
from ..models import Payment

class PaymentServiceFactory:
    _services = {
        Payment.PaymentProvider.STRIPE: StripeService,
        Payment.PaymentProvider.PAYPAL: PayPalService,
    }
    
    @classmethod
    def get_service(cls, provider: str) -> Optional[BasePaymentService]:
        service_class = cls._services.get(provider)
        if service_class:
            return service_class()
        return None 