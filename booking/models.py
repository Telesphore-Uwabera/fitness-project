from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created' and 'modified' fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class FitnessClass(TimeStampedModel):
    """
    Model representing a fitness class that users can book.
    """
    CLASS_TYPES = (
        ('yoga', _('Yoga')),
        ('pilates', _('Pilates')),
        ('hiit', _('HIIT')),
        ('cycling', _('Cycling')),
        ('strength', _('Strength Training')),
        ('dance', _('Dance')),
    )

    name = models.CharField(_('class name'), max_length=100)
    description = models.TextField(_('description'))
    instructor = models.CharField(_('instructor'), max_length=100)
    class_type = models.CharField(
        _('class type'),
        max_length=20,
        choices=CLASS_TYPES,
        default='yoga'
    )
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    capacity = models.PositiveIntegerField(_('capacity'))
    price = models.DecimalField(
        _('price'),
        max_digits=6,
        decimal_places=2,
        default=0.00
    )
    location = models.CharField(_('location'), max_length=200)
    is_active = models.BooleanField(_('active'), default=True)
    image = models.ImageField(
        _('class image'),
        upload_to='class_images/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('fitness class')
        verbose_name_plural = _('fitness classes')
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['class_type']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='end_time_after_start_time'
            ),
        ]

    def __str__(self):
        return f"{self.name} with {self.instructor} at {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def get_absolute_url(self):
        return reverse('class_detail', kwargs={'pk': self.pk})

    @property
    def duration(self):
        """Calculate duration in minutes"""
        return (self.end_time - self.start_time).total_seconds() / 60

    @property
    def spots_remaining(self):
        """Calculate remaining spots available"""
        return self.capacity - self.bookings.count()

    def is_full(self):
        return self.spots_remaining <= 0

    def is_upcoming(self):
        return self.start_time > timezone.now()


class Booking(TimeStampedModel):
    """
    Model representing a user's booking for a fitness class.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('user')
    )
    fitness_class = models.ForeignKey(
        FitnessClass,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('fitness class')
    )
    attended = models.BooleanField(_('attended'), default=False)
    cancelled = models.BooleanField(_('cancelled'), default=False)
    cancellation_reason = models.TextField(
        _('cancellation reason'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('booking')
        verbose_name_plural = _('bookings')
        ordering = ['-created']
        unique_together = ['user', 'fitness_class']
        indexes = [
            models.Index(fields=['user', 'fitness_class']),
        ]

    def __str__(self):
        return f"{self.user.username}'s booking for {self.fitness_class.name}"

    def get_absolute_url(self):
        return reverse('booking_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """Override save to send notifications"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.send_confirmation_email()
        elif self.cancelled and not is_new:
            self.send_cancellation_email()

    def send_confirmation_email(self):
        """Send booking confirmation email"""
        subject = _("Booking Confirmation: %(class_name)s") % {
            'class_name': self.fitness_class.name
        }
        
        context = {
            'user': self.user,
            'booking': self,
            'class': self.fitness_class,
        }
        
        text_message = render_to_string('emails/booking_confirmation.txt', context)
        html_message = render_to_string('emails/booking_confirmation.html', context)
        
        send_mail(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            html_message=html_message,
            fail_silently=False,
        )

    def send_cancellation_email(self):
        """Send booking cancellation email"""
        subject = _("Booking Cancelled: %(class_name)s") % {
            'class_name': self.fitness_class.name
        }
        
        context = {
            'user': self.user,
            'booking': self,
            'class': self.fitness_class,
            'reason': self.cancellation_reason,
        }
        
        text_message = render_to_string('emails/booking_cancellation.txt', context)
        html_message = render_to_string('emails/booking_cancellation.html', context)
        
        send_mail(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            html_message=html_message,
            fail_silently=False,
        )

    def cancel(self, reason=None):
        """Helper method to cancel a booking"""
        self.cancelled = True
        self.cancellation_reason = reason
        self.save()

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    health_notes = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"