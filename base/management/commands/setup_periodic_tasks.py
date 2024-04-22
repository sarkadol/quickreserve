from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

class Command(BaseCommand):
    help = 'Sets up periodic tasks'

    def handle(self, *args, **options):
        # Ensure the interval schedule is created
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=10,
            period=IntervalSchedule.SECONDS,
        )

        # Create the periodic task
        task, created = PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='Print every 10 seconds',  # Name of the periodic task
            task='base.tasks.print_every_10_seconds',  # Task to run, in the form 'app_name.tasks.task_function'
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created periodic task.'))
        else:
            self.stdout.write('Periodic task already exists.')

from django_celery_beat.models import PeriodicTask, IntervalSchedule

schedule, _ = IntervalSchedule.objects.get_or_create(
    every=10,
    period=IntervalSchedule.SECONDS,
)

PeriodicTask.objects.get_or_create(
    interval=schedule,
    name='Print every 10 seconds',
    task='base.tasks.print_every_10_seconds',
)
