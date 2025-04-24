from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from organizations.models import Organization
from django.utils import timezone

class ClientUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, **extra_fields)


class ClientUser(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
    ]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="client_users")
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    #phone_number = models.CharField(max_length=20)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notifications_enabled = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    objects = ClientUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']

    class Meta:
        unique_together = ['organization', 'email']

    def __str__(self):
        return f"{self.full_name} ({self.organization.code})"
