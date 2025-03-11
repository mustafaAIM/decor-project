from django.db import models
from django.utils.translation import gettext_lazy as _
from core.abstract.base import BaseModel
from authentication.models import User

class AuthAuditLog(BaseModel):
    class ActionType(models.TextChoices):
        LOGIN_SUCCESS = "LOGIN_SUCCESS", _("Login Success")
        LOGIN_FAILED = "LOGIN_FAILED", _("Login Failed")
        LOGOUT = "LOGOUT", _("Logout")
        PASSWORD_RESET_REQUEST = "PASSWORD_RESET_REQUEST", _("Password Reset Request")
        PASSWORD_RESET_SUCCESS = "PASSWORD_RESET_SUCCESS", _("Password Reset Success")
        ACCOUNT_LOCKED = "ACCOUNT_LOCKED", _("Account Locked")
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ActionType.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("auth audit log")
        verbose_name_plural = _("auth audit logs")
        ordering = ['-created_at'] 