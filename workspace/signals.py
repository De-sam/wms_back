# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking, Workspace
from django.utils.timezone import now

@receiver(post_save, sender=Booking)
def update_workspace_status_on_booking(sender, instance, **kwargs):
    if instance.status == 'ACTIVE' and instance.start_time <= now() <= instance.end_time:
        workspace = instance.workspace
        workspace.status = 'UNAVAILABLE'
        workspace.save()

@receiver(post_delete, sender=Booking)
def reset_workspace_status_on_delete(sender, instance, **kwargs):
    workspace = instance.workspace
    overlapping = Booking.objects.filter(
        workspace=workspace,
        status='ACTIVE',
        start_time__lte=now(),
        end_time__gte=now(),
    ).exists()

    if not overlapping:
        workspace.status = 'AVAILABLE'
        workspace.save()
