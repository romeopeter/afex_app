#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from afex_app.settings import base

# Set settings path
if base.DEBUG:
    env_settings = "afex_app.settings.development"
else:
    env_settings = "afex_app.settings.production"


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', env_settings)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
