
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response as DRFResponse


class ValidationErrorSerializer(serializers.Serializer):
    """
    DRF validation errors can be random. This serializer attempts
    to provide a better formatted interface for documentation purposes.
    """

    http_status_code = status.HTTP_400_BAD_REQUEST

    field_errors = serializers.DictField(
        required=False,
        help_text="Validation field errors"
    )

    non_field_errors = serializers.ListField(
        child=serializers.CharField(), required=False,
        help_text="Validation non-field errors"
    )

    error_code = serializers.CharField(
        default="validation_error", read_only=True,
        help_text="Error code."
    )

    def __init__(self, instance=None, data=None, **kwargs):
        self._initial_data = data
        if data:
            data = self.parse_data(data)
        super().__init__(instance, data, **kwargs)


    def __call__(self):
        return self.json_response()

    def parse_data(self, data: dict) -> dict:
        """Parse input data to serializer format"""

        final_dict = {}
        non_field_errors = data.pop("non_field_errors", None)
        if non_field_errors:
            final_dict["non_field_errors"] = non_field_errors
        if data:
            # put data dict behind a dictionary key
            final_dict["field_errors"] = data
        
        return final_dict
        
    def json_response(self) -> DRFResponse:
        # if validation fails, return original data
        if self.is_valid():
            return DRFResponse(self.data, self.http_status_code)
        else:
            return DRFResponse(self._initial_data, self.http_status_code)



class URLParamsValidationErrorSerializer(ValidationErrorSerializer):

    """Validation error interface for URL params"""

    error_code = serializers.CharField(
        default="urlparams_validation_error", read_only=True,
        help_text="Error code."
    )