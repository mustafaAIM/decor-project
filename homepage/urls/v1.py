from django.urls import path
from ..views.homepage_view import homepage_data

urlpatterns = [
    path('homepage/', homepage_data, name='homepage_data'),
]
