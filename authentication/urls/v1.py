from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
#views
from authentication.views import *

app_name = 'v1'

urlpatterns = [
    path("register/", RegisterViewSet.as_view({"post": "create"}), name="register"),
    path("verification/", RegisterViewSet.as_view({"post": "verify"}), name="verification"),
    path("resend-otp/", RegisterViewSet.as_view({"post": "resend"}), name="resend-otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("password-reset-request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset-verify/", PasswordResetVerifyOTPView.as_view(), name="password-reset-verify"),
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    
  
]