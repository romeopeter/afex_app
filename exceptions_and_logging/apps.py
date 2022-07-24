from typing import Iterable

from django.apps import AppConfig


class ExceptionsAndLoggingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exceptions_and_logging'

    def ready(self) -> None:
        from django.conf import settings
        from .exceptions import MissingErrorEmailRecepients, MissingErrorSenderEmail

        # confirm that settings are properly configured
        email_recepients = getattr(settings, "EXC_EMAIL_RECEPIENTS", [])
        if not isinstance(email_recepients, Iterable) or not email_recepients:
            raise MissingErrorEmailRecepients(
                "No error email recepients found.\n"
                "Add a list of emails to constant 'EXC_EMAIL_RECEPIENTS' "
                "in your django settings module."
            )

        sender_email = getattr(settings, "EXC_SENDER_EMAIL", None)
        if sender_email is None:
            raise MissingErrorSenderEmail(
                "No error sender email found.\n"
                "Add an email to constant 'EXC_SENDER_EMAIL' "
                "in your django settings module."
            )
