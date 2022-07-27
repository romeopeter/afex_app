"""
For the scope of this app, all tasks are synchronous, but
this module allows for easy implementation of asynchronous tasks
using tools like Celery.

As a result, functions are first order and kwargs are JSON serializable.
"""

from django.core.mail import send_mail


def task_send_confirmation_pin_email(**kwargs):
    """Send confirmation pin email

    Parameters
    ----------
    first_name: str
        User first name
    confirmation_pin: str
        User confirmation pin
    email: str
        User email
    """
    
    first_name, confirmation_pin = kwargs["first_name"], kwargs["confirmation_pin"]
    email = kwargs["email"]

    msg =   f"Hello {first_name}!\n" \
            f"Welcome to Afex App, please use this pin to confirm your account {confirmation_pin}."

    send_mail(
        from_email="app@afex.com",
        subject="OTP - Activate your Afex account.",
        message=msg,
        recipient_list=[email]
    )