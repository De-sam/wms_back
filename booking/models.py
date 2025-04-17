import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

WORKSPACE_TYPES = [
    ('desk', 'Desk'),
    ('meeting_room', 'Meeting Room'),
    ('private_office', 'Private Office'),
    ('training_table', 'Training Table'),
]

AMENITY_OPTIONS = [
    ('power_outlet', 'Power Outlet'),
    ('projector', 'Projector'),
    ('whiteboard', 'Whiteboard'),
    ('ergonomic_chair', 'Ergonomic Chair'),
]

class Organization(models.Model):
    name = models.CharField(max_length=255)
    org_code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.city}, {self.state} ({self.organization.name})"


class Section(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.location.city}"


class Workspace(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="workspaces")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=WORKSPACE_TYPES)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    amenities = models.JSONField(default=list, blank=True)  # Use frontend checkbox to fill this
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Seat(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='seats')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    identifier = models.CharField(max_length=100, unique=True)  # e.g. "VIP_A1_Desk01"

    def __str__(self):
        return self.identifier


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="active")  # can be extended, cancelled etc.

    def __str__(self):
        return f"{self.user.email} - {self.seat.identifier} on {self.date}"

    class Meta:
        unique_together = ('seat', 'date', 'start_time', 'end_time')  # basic conflict prevention
