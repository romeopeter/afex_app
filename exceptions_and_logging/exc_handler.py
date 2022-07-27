import logging
from typing import Union

from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.conf import settings

from celery import shared_task

from rest_framework import status
from rest_framework.views import set_rollback
from rest_framework.response import Response
from rest_framework import exceptions as drf_exceptions

from .logging import get_extra_kwargs, parse_email_message

import exceptions_and_logging.exceptions as app_exceptions
from exceptions_and_logging.logging import stream_log_handler, base_formatter
import exceptions_and_logging.tasks as exc_tasks

# types
app_or_python_errors = Union[app_exceptions.BaseAppException, Exception]

# set up logging
logger = logging.Logger(__name__)
stream_log_handler = stream_log_handler
stream_log_handler.setFormatter(base_formatter)
logger.addHandler(stream_log_handler)


def log_and_send_mail(exc: app_or_python_errors, extra_kwargs, allow_async=False):
    if isinstance(exc, app_exceptions.BaseAppException):
        # log only server errors
        if str(exc.http_status_code).startswith("5"):
            exc.logger.error(exc.error_msg, extra=extra_kwargs)
            
        # check for instructions to send mail
        if getattr(exc, "notify_via_mail", False):
            extra_kwargs.update({"message": exc.error_msg})
            email_msg = parse_email_message(extra_kwargs)
            exc.send_error_mail(custom_message=email_msg)
    else:
        message = str(exc)
        logger.exception(message, extra=extra_kwargs)
        extra_kwargs.update({"message": message})
        email_msg = parse_email_message(extra_kwargs)
        if allow_async:
            exc_tasks.send_error_mail.delay(email_msg)
        else:
            exc_tasks.send_error_mail(email_msg)



def app_exception_handler(exc: Exception, context):
    """Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """

    extra_kwargs = get_extra_kwargs(context, exc)


    if isinstance(exc, Http404):
        exc = app_exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = app_exceptions.Unauthorized()

    # handler for drf exceptions
    if isinstance(exc, drf_exceptions.APIException):
        # basically parses the response to be uniform to the applictions
        # error reporting format.
        extra_kwargs.update({"error_source" : "DRF"})
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, (list, dict)):
            data = {
                "message": str(exc.detail),
                "error_type": exc.__class__.__name__,
                "error_code": "validation_error"
            }
        else:
            data = {
                "message": str(exc.detail), "error_type": exc.__class__.__name__,
                "error_code": exc.detail.code,
            }
        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)
    
    # handler for application exceptions
    elif isinstance(exc, app_exceptions.BaseAppException):
        extra_kwargs.update({"error_source" : "Application"})
        set_rollback()
        log_and_send_mail(exc, extra_kwargs)
        return Response(exc.data, status=exc.http_status_code)

    # handler for uncaught application errors
    else:
        # Log these errors and send developer an email but don't
        # return details of this error to the client as it is an
        # internal issue.
        extra_kwargs.update({"error_source" : "Python"})

        data = {
            "message": "A server error occured", "error_type": "",
            "error_code": "internal_server_error"
        }

        set_rollback()
        log_and_send_mail(exc, extra_kwargs)

        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)