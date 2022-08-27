import importlib

from rest_framework_simplejwt.authentication import JWTAuthentication

from common_app.utils.general_utils import app_settings


online_status_policy = app_settings["ONLINE_STATUS_POLICY"]
policy_module_path = "registration.policies"


def get_online_policy_class():
    policy_module = importlib.import_module(policy_module_path)
    return getattr(policy_module, online_status_policy)


class CustomAuthBackend(JWTAuthentication):
    """
    Overriden basically to persist a time bound key/value pair on
    Redis for verification of user's online status based on the
    application's online status policies.
    """

    def authenticate(self, request):
        if (auth_value:= super().authenticate(request)) is not None:
            user, validated_token = auth_value
            online_policy = get_online_policy_class()(user, validated_token)
            online_policy.set_key()
            return user, validated_token
        else:
            return 