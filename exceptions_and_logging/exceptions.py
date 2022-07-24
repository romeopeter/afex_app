import logging
from typing import List
from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response

import exceptions_and_logging.logging as app_logging
import exceptions_and_logging.tasks as exc_taks


class MissingErrorEmailRecepients(Exception):
    pass

class MissingErrorSenderEmail(Exception):
    pass



class BaseAppException(Exception):
    """
    Base exception for this application.
    All application errors should inherit from this class.
    """

    _http_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_error_msg = _('A server error occurred.')
    default_error_code = "application_error"
    default_hint = None
    ERROR_SOURCE = "Application"

    def __init__(
        self, error_msg=None, error_code=None, http_status_code=None,
        hint=None, notify_via_mail=False, module: str = None, show_err_type=False,
        cause: str = None
    ):
        self.error_msg = error_msg or self.default_error_msg
        self.error_code = error_code or self.default_error_code
        self.http_status_code = http_status_code or self._http_status_code
        self.hint = hint or self.default_hint
        self.module = module
        self.logger = self.get_logger()
        self.notify_via_mail = notify_via_mail
        self.sender_email = settings.EXC_SENDER_EMAIL
        self.email_recepients = settings.EXC_EMAIL_RECEPIENTS
        self.show_err_type = show_err_type
        # underlying cause of the error if reported by another.
        # used only for email reporting, shouldn't be sent to client 
        self.cause = cause

    @property
    def data(self) -> dict:
        data = OrderedDict({
            "message": self.error_msg,
            "error_code": self.error_code,
        })
        if self.show_err_type:
            data.update({"error_type": self.__class__.__name__})
        if self.hint is not None:
            data.update({"hint": self.hint})
        
        return data

    def get_logger(self) -> logging.Logger:
        logger = logging.Logger("-") if self.module is None else logging.Logger(self.module)
        stream_log_handler = app_logging.stream_log_handler
        stream_log_handler.setFormatter(app_logging.base_formatter)
        logger.addHandler(stream_log_handler)
        return logger

    def send_error_mail(
        self, context: dict = None, custom_message=None, custom_recepients=None,
        allow_async=True
    ):
        # parameter checks
        assert_msg = "'context' or 'custom message must be provided'."
        assert context or custom_message, assert_msg
        
        if context:
            extra_kwargs = app_logging.get_extra_kwargs(context, self)
            email_msg = app_logging.parse_email_message(extra_kwargs)
        else:
            email_msg = custom_message

        recepients = custom_recepients or self.email_recepients

        if allow_async:
            exc_taks.send_error_mail.delay(
                email_msg, recepients, self.error_code
            )
        else:
            exc_taks.send_error_mail(
                email_msg, recepients, self.error_code
            )   

    def log_and_send_error_mail(self, context):
        extra_kwargs = app_logging.get_extra_kwargs(context, self)
        extra_kwargs.update({"error_source": self.ERROR_SOURCE})
        self.logger.error(msg=self.error_msg, extra=extra_kwargs)
        extra_kwargs.update({"message": self.error_msg})
        email_msg = app_logging.parse_email_message(extra_kwargs)
        self.send_error_mail.delay(email_msg)

    def json_response(self, show_err_type=False) -> Response:
        self.show_err_type = show_err_type
        return Response(
            self.data, status=self.http_status_code
        )

    @property
    def kwargs(self):
        return {
            "error_msg": self.error_msg, "error_code": self.error_code,
            "http_status_code": self.http_status_code, "hint": self.hint,
            "module": self.module, "logger": self.logger,
            "send_mail": self.send_error_mail,
        }


    def __str__(self) -> str:
        return str(self.data)


class GenericError(BaseAppException):
    
    """Feel free to customize parameters."""
    

class NotFound(BaseAppException):
    _http_status_code = status.HTTP_404_NOT_FOUND
    default_error_msg = _('Requested resource not found.')
    default_error_code = 'not_found'


class BadRequest(BaseAppException):
    _http_status_code = status.HTTP_400_BAD_REQUEST
    default_error_msg = _('Request not properly formed.')
    default_error_code = 'bad_request'


class Unauthorized(BaseAppException):
    """Used basically for failed authentications/authorizations"""

    _http_status_code = status.HTTP_401_UNAUTHORIZED
    default_error_msg = _(
        'You do not have required permissions to perform this action.'
    )
    default_error_code = 'permission_denied'


class Forbidden(BaseAppException):
    """
    Used model/object level pemission denials even after successful
    authentication.
    """

    _http_status_code = status.HTTP_403_FORBIDDEN
    default_error_msg = _(
        'You do not have required permissions to perform this action.'
    )
    default_error_code = 'forbidden'


class UnsuccessfulRequest(BaseAppException):
    _http_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_error_msg = _('Request was unsuccessful')
    default_error_code = "unsuccesful_request"


class IntegrityError(BaseAppException):
    """Errors as a result of database integrity errors."""

    _http_status_code = status.HTTP_409_CONFLICT
    default_error_msg = "'%s' has a conflicting value. "
    default_error_code = "conflict"

    def __init__(self, field: str, **kwargs):
        msg = self.default_error_msg % field
        kwargs["error_msg"] = msg
        super().__init__(**kwargs)
