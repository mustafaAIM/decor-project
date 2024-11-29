from abc import ABC, abstractmethod
from typing import Dict, Any
from ..models import Payment

class BasePaymentService(ABC):
    """Abstract base class for payment services"""
    
    @abstractmethod
    def create_payment_intent(self, payment: Payment) -> Dict[str, Any]:
        """Create a payment intent with the payment provider"""
        pass
    
    @abstractmethod
    def process_webhook(self, payload: Dict[str, Any]) -> None:
        """Process webhook events from the payment provider"""
        pass
    
    @abstractmethod
    def refund_payment(self, payment: Payment) -> bool:
        """Refund a payment"""
        pass
    
    @abstractmethod
    def verify_payment(self, payment: Payment) -> bool:
        """Verify a payment's status"""
        pass