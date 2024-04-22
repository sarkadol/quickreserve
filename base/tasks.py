from celery import shared_task
from .models import Reservation, ReservationSlot
from django.utils import timezone
from django.core.mail import send_mail
from datetime import datetime, timedelta

@shared_task
def delete_unused_slots():
    # Define your logic here for finding and deleting unused slots
    # For example, delete slots that are marked as 'available' and are older than 1 hour
    now = timezone.now()
    """ReservationSlot.objects.filter(
        status='available', start_time__lt=now - timezone.timedelta(hours=1)
    ).delete()"""
    print(f"Running delete_unused_slots task at {timezone.now()}")

@shared_task
def send_reservation_reminder():
    tomorrow = timezone.now().date() + timedelta(days=1)
    reservations = Reservation.objects.filter(start_date=tomorrow)
    print("send reservation reminder task")
    for reservation in reservations:
        print(reservation)
        """send_mail(
            'Reminder: Upcoming Reservation',
            f'Hi, this is a reminder that your reservation for {reservation.item_name} is scheduled for {reservation.start_date}.',
            'from@example.com',
            [reservation.user.email],
            fail_silently=False,
        )"""


@shared_task
def print_every_10_seconds():
    print("Hello, every 10 seconds!")
        