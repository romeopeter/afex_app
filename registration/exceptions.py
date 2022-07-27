from rest_framework import status

from exceptions_and_logging.exceptions import BaseAppException


class UnconfirmedUserError(BaseAppException):
    """Raised when unconfirded users try to access protected rewsources"""

    _http_status_code = status.HTTP_401_UNAUTHORIZED
    default_error_msg = "User unconfirmed"
    default_error_code = "unconfirmed_user"
    default_hint = "Try confirming user via pin method."