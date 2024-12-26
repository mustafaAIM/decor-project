from django.urls import path
from ..views.notification_view import NotificationViewSet

urlpatterns = [
    path('notifications/', NotificationViewSet.as_view({'get': 'list'}), name='notification-list'),
]