"""
WSGI config for afex_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from .settings.base import DEBUG


if DEBUG:
    env_settings = "afex_app.settings.developent"
else:
    env_settings = "afex_app.settings.production"


os.environ.setdefault("DJANGO_SETTINGS_MODULE", env_settings)

application = get_wsgi_application()
