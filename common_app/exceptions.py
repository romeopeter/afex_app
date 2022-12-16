from django.utils.translation import gettext_lazy as _

from rest_framework import status

from exceptions_and_logging.exceptions import BaseAppException


class ExpiredCredentialError(BaseAppException):

    _http_status_code = status.HTTP_401_UNAUTHORIZED
    default_error_msg = _("The given credential has expired.")
    default_error_code = _("credential_expired")
    default_hint = _("Kindly make a request for another.")