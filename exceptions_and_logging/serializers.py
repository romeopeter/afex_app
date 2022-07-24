from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    """Error serializer for schema definitions"""

    message = serializers.CharField(
        help_text=_("Error message")
    )

    error_type = serializers.CharField(
        allow_blank=True, required=False,
        help_text=_(
            "Error type e.g. WalletUpdateError. "
            "It can be blank in internal server errors."
        )
    )

    error_code = serializers.CharField(
        help_text=_("Error code e.g. unsuccessful_request")
    )

    hint = serializers.CharField(
        required=False,
        help_text=_("Suggestions on how to fix issue.")
    )   

