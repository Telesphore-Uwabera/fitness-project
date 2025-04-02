#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import dotenv
from pathlib import Path


def main():
    """Run administrative tasks."""
    
    # Load environment variables from .env file
    dotenv.load_dotenv(
        os.path.join(Path(__file__).resolve().parent.parent, '.env'
    )
    
    # Set the default Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_project.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Add custom commands
    try:
        from django.core.management.commands.runserver import Command as runserver
        runserver.default_port = os.getenv('DJANGO_DEFAULT_PORT', '8000')
        runserver.default_addr = os.getenv('DJANGO_DEFAULT_HOST', '0.0.0.0')
    except ImportError:
        pass
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()