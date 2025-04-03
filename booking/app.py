import booking.signals
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BookingConfig(AppConfig):
    """
    Application configuration for the booking app.
    
    This class defines metadata and configuration for the booking application.
    It's referenced in INSTALLED_APPS as 'booking.apps.BookingConfig'.
    """

    # The default auto field to use for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    
    # The name of the application (Python path format)
    name = 'booking'
    
    # Human-readable name for the application
    verbose_name = _('Fitness Class Booking System')
    
    # Application icon (Font Awesome class name, optional)
    icon = 'fa-calendar-check-o'
    
    # App ordering in admin index (optional)
    order = 100
    
    def ready(self):
        """
        Override this method to perform initialization tasks when Django starts.
        Called as soon as the registry is fully populated.
        """
        # Import signal handlers
        self._register_signals()
        
        # Initialize background tasks
        self._initialize_scheduled_tasks()
        
        # Register custom checks
        self._register_checks()
    
    def _register_signals(self):
        """Register all signal handlers for the application."""
        # Import signals module to connect handlers
        from . import signals  # noqa
    
    def _initialize_scheduled_tasks(self):
        """
        Initialize any background tasks needed for the application.
        Uses django-background-tasks if available.
        """
        try:
            from background_task.models import Task
            from .tasks import send_reminders
            
            if not Task.objects.filter(task_name='booking.tasks.send_reminders').exists():
                send_reminders(repeat=Task.DAILY, verbose_name="Daily booking reminders")
        except ImportError:
            # Background tasks not configured
            pass
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to initialize scheduled tasks: {e}")
    
    def _register_checks(self):
        """Register custom system checks for this application."""
        from django.core.checks import register
        from .checks import (
            check_configuration,
            check_email_settings,
            check_booking_policies
        )
        
        register(check_configuration)
        register(check_email_settings)
        register(check_booking_policies)

    def __init__(self, app_name, app_module):
        """Initialize the application configuration."""
        super().__init__(app_name, app_module)
        # Any additional initialization can go here