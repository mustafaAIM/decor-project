from django.urls import path
from ..views.dashboard_view import dashboard_data

urlpatterns = [
    path('dashboard/', dashboard_data, name='dashboard_data'),
]
