from celery import shared_task
from .models import ReservationSlot
from django.utils import timezone

@shared_task
def delete_unused_slots():
    # Define your logic here for finding and deleting unused slots
    # For example, delete slots that are marked as 'available' and are older than 1 hour
    now = timezone.now()
    ReservationSlot.objects.filter(
        status='available', start_time__lt=now - timezone.timedelta(hours=1)
    ).delete()
    print(f"Running delete_unused_slots task at {timezone.now()}")
