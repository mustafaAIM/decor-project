from django.urls import path
from ..views import PaymentViewSet
from ..views.webhook_views import stripe_webhook

urlpatterns = [
    path('payments/', PaymentViewSet.as_view({'get': 'list'}), name='payment-list'),
    path('payments/stripe-success/', PaymentViewSet.as_view({'post': 'stripe_success'}), name='stripe-success'),
    path('payments/<uuid:uuid>/', PaymentViewSet.as_view({'get': 'retrieve'}), name='payment-detail'),
    path('payments/create-intent/', PaymentViewSet.as_view({'post': 'create_payment_intent'}), name='create-payment-intent'),
    path('payments/paypal-success/', PaymentViewSet.as_view({'get': 'paypal_success'}), name='paypal-success'),
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
]
