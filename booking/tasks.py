from background_task import background
from django.utils import timezone
from .models import Booking

@background(schedule=60)
def send_reminders():
    """Send reminders for upcoming classes."""
    now = timezone.now()
    upcoming = Booking.objects.filter(
        fitness_class__start_time__range=(now, now + timedelta(hours=24)),
        cancelled=False,
        reminder_sent=False
    )
    # Implement reminder logic