from django.db import models
from django.utils import timezone
from django.conf import settings
from organizations.models import Organization



class Section(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="sections",
        null=True,     # ✅ allow null in database
        blank=True     # ✅ allow empty in forms/admin
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sections"
    )

    def __str__(self):
        return self.name


class Workspace(models.Model):
    WORKSPACE_TYPE_CHOICES = (
            ("Desk", "Desk"),
            ("Room", "Room"),
            ("Office", "Office"),
            ("Hall", "Hall"),
            ("Others", "Others"),
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="workspaces"
    )
    name = models.CharField(max_length=100)
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
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    user = models.ForeignKey(
        settings.CLIENT_USER_MODEL,
        on_delete=models.CASCADE
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.workspace.name} booked by {self.user.username}"
