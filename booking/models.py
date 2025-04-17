import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Organization(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True)  # for subdomain or identification

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="employees")
    role = models.CharField(max_length=20, choices=(("Admin", "Admin"), ("Learner", "Learner")))

    def __str__(self):
        return self.user.get_full_name()


class Location(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    address = models.TextField()
    total_capacity = models.PositiveIntegerField()
    employees = models.ManyToManyField(Employee, blank=True, related_name="assigned_locations")

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"


class WorkspaceSection(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=100)  # e.g., VIP, Regular
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.location.name})"


class Workspace(models.Model):
    WORKSPACE_TYPE_CHOICES = (
        ("Desk", "Desk"),
        ("Meeting Room", "Meeting Room"),
        ("Private Office", "Private Office"),
        ("Training Table", "Training Table"),
    )
    AMENITY_OPTIONS = [
        ('power_outlet', 'Power Outlet'),
        ('projector', 'Projector'),
        ('whiteboard', 'Whiteboard'),
        ('ergonomic_chair', 'Ergonomic Chair'),
    ]
    section = models.ForeignKey(WorkspaceSection, on_delete=models.CASCADE, related_name="workspaces")
    name = models.CharField(max_length=100)  # e.g., Desk A1, Room B2
    type = models.CharField(max_length=50, choices=WORKSPACE_TYPE_CHOICES)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    amenities = models.JSONField(default=list, blank=True, choices=AMENITY_OPTIONS)  # ["Whiteboard", "Power Outlet"]
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Seat(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="seats")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    identifier = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.identifier} - {self.workspace.name}"

class Booking(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="bookings")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="bookings")
    date = models.DateField(default=timezone.now)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="active")

    class Meta:
        unique_together = ('seat', 'date', 'start_time', 'end_time')  # Avoid double booking

    def __str__(self):
        return f"{self.user.user.email} booked {self.seat} from {self.start_time} to {self.end_time}"