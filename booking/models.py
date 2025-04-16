from django.db import models
from organizations.models import Organization
from users.models import EmployeeUser  # Assuming this is the employee model
from django.utils.crypto import get_random_string
import uuid

class Location(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="locations")
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    capacity = models.PositiveIntegerField()
    employees = models.ManyToManyField(EmployeeUser, related_name="locations")

    def __str__(self):
        return f"{self.city}, {self.state} - {self.address}"


class Section(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=100)  # e.g. "VIP", "Regular"
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} - {self.location.city}"


class Seat(models.Model):
    section = models.ForeignKey('Section', on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)  # unique within section
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        unique_together = ('section', 'seat_number')

    def __str__(self):
        return f"{self.section.name} - {self.seat_number}"

    def save(self, *args, **kwargs):
        if not self.uuid:
            location = self.section.location
            raw_string = f"{location.id}-{self.section.id}-{self.seat_number}-{get_random_string(6)}"
            self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, raw_string)
        super().save(*args, **kwargs)
