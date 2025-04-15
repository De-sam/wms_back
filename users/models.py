from django.db import models
from organizations.models import Organization
from django.contrib.auth.hashers import make_password, check_password

class ClientUser(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="client_users")
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128, null=True, blank=True)  # store hashed password

    class Meta:
        unique_together = ['organization', 'email']

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.full_name} ({self.organization.code})"
    