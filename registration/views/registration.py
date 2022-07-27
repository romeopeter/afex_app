"""
All registration views
"""

# third party apps
from django.db import transaction

# drf
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# drf spectacular
from drf_spectacular.utils import (
    extend_schema, OpenApiResponse,
)

# project based django apps
from common_app.serializers import ValidationErrorSerializer
from exceptions_and_logging.serializers import ErrorSerializer

# current app
from ..serializers import (
    SignUpSerializer, UserDisplaySerializer,
    SignInSerializer, IntegrityErrorSerializer,
)
from ..serializers import IntegrityErrorSerializer

from ..utils import SignUpWithPin
from ..exceptions import UnconfirmedUserError


# sign up: /v1/registration/sign_up
class RegistrationViewsets(GenericViewSet):

    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            201: OpenApiResponse(SignUpSerializer, "Sign up successful"),
            409: OpenApiResponse(
                IntegrityErrorSerializer, "Already existing email"
            ),
            400: OpenApiResponse(ValidationErrorSerializer, "Validation errors"),
        }
    )
    @action(methods=["post"], detail=False, serializer_class=SignUpSerializer)
    def sign_up(self, request):
        """Sign-up User"""

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # return 409 conflict response if integrity error noticed
            if (integrity_ser := IntegrityErrorSerializer(data=serializer.errors)._is_valid()):
                return integrity_ser.http_response_409()
            
            # return 400 for other validation errors
            return ValidationErrorSerializer(data=serializer.errors).json_response()


    @extend_schema(
        request=TokenObtainPairSerializer,
        responses={
            200: OpenApiResponse(SignInSerializer, "Successfully logged in"),
            401: OpenApiResponse(ErrorSerializer, "Wrong credentials or user unconfirmed"),
        }
    )
    @action(methods=["post"], detail=False, serializer_class=TokenObtainPairSerializer)
    def sign_in(self, request, *args, **kwargs):
        """
        Sign in to user account
        """

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        except UnconfirmedUserError as err:
            return err.json_response()

        user = serializer.user
        user_ser = UserDisplaySerializer(user)

        token_resp_params = {
            "access": serializer.validated_data["access"],
            "refresh": serializer.validated_data["refresh"]
        }

        sign_in_ser_data = {
            "user": user_ser.data,
            "tokens": token_resp_params
        }

        return Response(sign_in_ser_data, status=status.HTTP_200_OK)
