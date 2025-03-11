from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from core.abstract.base import BaseModel

class UserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def with_deleted(self):
        return super().get_queryset()

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set."))
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.DEVELOPER)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser must have is_staff=True."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        DEVELOPER = "DEVELOPER", _("Developer")
        CUSTOMER = "CUSTOMER", _("Customer")

    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=50)
    last_name = models.CharField(_("last name"), max_length=50)
    phone = models.CharField(_("phone number"), max_length=15, blank=True, null=True)
    address = models.TextField(_("address"), blank=True, null=True)
    is_active = models.BooleanField(_("active"), default=False)
    is_staff = models.BooleanField(_("staff status"), default=False)
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    role = models.CharField(
        _("role"), 
        max_length=10, 
        choices=Role.choices, 
        default=Role.CUSTOMER
    )
    otp = models.CharField(_("otp"), max_length=6, null=True, blank=True)
    otp_exp = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(_("image"), upload_to='users/', blank=True, null=True)
    last_password_change = models.DateTimeField(null=True, blank=True)
    locked_until = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    def is_otp_expired(self): 
        if not self.otp_exp:
            return True
        print(self.otp_exp  )
        print(timezone.now()) 
        print(self.otp_exp < timezone.now() - timedelta(minutes=10))
        return self.otp_exp < timezone.now() - timedelta(minutes=10)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_developer(self):
        return self.role == self.Role.DEVELOPER

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False