from django.db import models
from django.utils import timezone
from django.conf import settings
import django.utils.timezone as timezone

class Workspace(models.Model):
    WORKSPACE_TYPE_CHOICES = (
            ("Desk", "Desk"),
            ("Room", "Room"),
            ("Office", "Office"),
            ("Hall", "Hall"),
            ("Others", "Others"),
    )

    name = models.CharField(max_length=100)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='workspaces')
    type = models.CharField(max_length=50, choices=WORKSPACE_TYPE_CHOICES)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    amenities = models.JSONField(default=list, blank=True)  # Removed strict validation

    def __str__(self):
        return f"{self.name} ({self.section.name})"

    @property
    def is_available(self):
        now = timezone.now()
        return not self.bookings.filter(start_time__lte=now, end_time__gte=now).exists()


class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    user = models.ForeignKey(
        settings.CLIENT_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(default=timezone.now)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.workspace.name} booked by {self.user.full_name}"
    