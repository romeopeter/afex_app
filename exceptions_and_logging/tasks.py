import logging
from typing import List

from django.conf import settings
from django.core.mail import send_mail

from celery import shared_task

from .logging import stream_log_handler, base_formatter


# set up logging
logger = logging.Logger(__name__)
stream_log_handler = stream_log_handler
stream_log_handler.setFormatter(base_formatter)
logger.addHandler(stream_log_handler)


@shared_task
def send_error_mail(
    email_msg: str, recepients: List[str] = None, subject: str = None
):
    subject = subject or "Application Error"
    recepients = recepients or settings.EXC_EMAIL_RECEPIENTS

    try:
        send_mail(
            subject=subject, message=email_msg,
            from_email=settings.EXC_SENDER_EMAIL, recipient_list=recepients
        )
    except Exception as err:
        # log this error but allow application proceed
        logger.exception(f"Error mail not sent because: {err}")
