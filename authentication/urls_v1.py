from django.urls import path , include
from rest_framework.routers import DefaultRouter
#views
from authentication.views import *

urlpatterns = [
  path("register/",RegisterViewSet.as_view({"post":"create"})),
  path("verification/",RegisterViewSet.as_view({"post":"verify"})),
  path("resend-otp/",RegisterViewSet.as_view({"post":"resend"})),
  path("login/",LoginView.as_view()),
]