import colorlog
import traceback

from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.request import Request

stream_log_handler = colorlog.StreamHandler()

log_format = \
    """
%(log_color)s%(asctime)s  %(levelname)s  %(name)s  %(error_type)s  %(error_source)s
%(message)s
%(log_color)s%(user_id)s  %(request_path)s %(module_name)s  %(view_name)s

-------Hint-------
%(hint)s

Traceback Info
--------------
%(traceback)s
"""

base_formatter = colorlog.ColoredFormatter(
	log_format,
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# stream_log_handler.setFormatter(formatter)


error_email_format = \
"""
Time of error: %(asctime)s
Level: %(levelname)s
Error Type: %(error_type)s
Error Source: %(error_source)s
Module name: %(module_name)s
User ID: %(user_id)s
Request Url: %(request_path)s
View Name: %(view_name)s

-------Message-------
%(message)s

-------Hint-------
%(hint)s

-------Traceback------
%(traceback)s

-------Underlying Cause------
%(cause)s
"""


def get_extra_kwargs(context: dict, exc) -> dict:
    """Extra kwargs used for log and email formatter.
    
    Parameters
    ----------
    context: dict
        A dictionary containing 'request' and 'view' keys representing the
        request obj and the view object.
    exc: Exception
        The exception to be reported.
    """

    module_name = getattr(exc, "module", None) or "-"
    view = context.get("view")
    request: Request = context.get("request")
    user = request.user
    request_path = get_current_site(request).domain + request._request.path
    hint = getattr(exc, "hint", None)

    if isinstance(user, AnonymousUser):
        user_id = "AnonymousUser"
    else:
        user_id = getattr(settings, "EXC_USERNAME_FIELD", None) \
                    or getattr(user, "USERNAME_FIELD", user.id)

    extra = {
        "user_id": user_id, "request_path": request_path, "error_source": "-",
        "view_name": view.__class__.__name__, "module_name": module_name,
        "traceback": traceback.format_exc(), "error_type": exc.__class__.__name__,
        "hint": hint, "cause": getattr(exc, "cause", None) or "-"
    }
    return extra

def parse_email_message(extra_kwargs: dict, levelname="ERROR") -> str:
    mail_kwargs = {
        "asctime": str(timezone.now()), "levelname": levelname,
        **extra_kwargs,
    }
    return error_email_format % mail_kwargs
