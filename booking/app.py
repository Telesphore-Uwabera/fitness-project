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
        # Import signal handlers to ensure they're registered
        from . import signals  # noqa
        
        # Initialize any periodic tasks (e.g., for sending reminders)
        self._initialize_scheduled_tasks()
        
        # Register custom admin checks
        self._register_checks()
    
    def _initialize_scheduled_tasks(self):
        """
        Initialize any background tasks needed for the application.
        """
        try:
            from background_task.models import Task
            from .tasks import send_reminders
            
            # Check if reminders task already exists
            if not Task.objects.filter(task_name='booking.tasks.send_reminders').exists():
                send_reminders(repeat=Task.DAILY)
        except ImportError:
            # Background tasks not configured, skip initialization
            pass
        except Exception as e:
            # Log error but don't prevent app startup
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to initialize scheduled tasks: {e}")
    
    def _register_checks(self):
        """
        Register custom system checks for this application.
        """
        from django.core.checks import register
        from .checks import check_configuration
        
        register(check_configuration)