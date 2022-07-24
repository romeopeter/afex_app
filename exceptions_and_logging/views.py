from django.http.response import JsonResponse

from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.views import APIView
from rest_framework.response import Response

from .exceptions import BaseAppException


class DRFView(APIView):

    def post(self, request, **kwargs):
        error_type = kwargs.get("error_type")
        message = request.data["message"]
        if error_type == "python":
            raise TypeError(message)
        elif error_type == "drf_regular":
            raise ParseError(message)
        elif error_type == "drf_validation":
            raise ValidationError({"field": message, "field_2": message})
        elif error_type == "exc_and_log":
            raise BaseAppException(
                error_msg=message, module=__name__, notify_via_mail=True,
                hint="Dont try this again...kidding"
            )
        else:
            return Response({})

    


