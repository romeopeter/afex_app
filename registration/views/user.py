"""
All user views
"""

# Django
from django.contrib.auth import get_user_model

# drf
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    DestroyModelMixin, RetrieveModelMixin, ListModelMixin
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from rest_framework_simplejwt.authentication import JWTAuthentication


# drf spectacular
from drf_spectacular.utils import (
    extend_schema, OpenApiResponse, OpenApiTypes
)

# project based django apps
from common_app.pagination import GeneralPagingation, paginator_header_params
from common_app.serializers import URLParamsValidationErrorSerializer, ValidationErrorSerializer
from common_app.utils.general_utils import app_settings

from exceptions_and_logging.serializers import ErrorSerializer

# current app
from ..serializers import (
    UserDisplaySerializer, BriefUserDisplaySerializer, AddFriendsSerializer,
    SearchUrlParamsSerializer, UIOpenSerializer, OnlineUserDisplaySerializer
)

from ..policies import UIOpenIsOnline


class UserViewsets(
    DestroyModelMixin, ListModelMixin,
    RetrieveModelMixin, GenericViewSet
):

    permission_classes = [IsAuthenticated]
    serializer_class = UserDisplaySerializer
    queryset = get_user_model().objects.all()
    pagination_class = GeneralPagingation

    @extend_schema(
        responses={
            200: OpenApiResponse(UserDisplaySerializer, "Success"),
            404: OpenApiResponse(ErrorSerializer, "User not found")
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a user"""

        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        parameters=[*paginator_header_params],
        responses={
            200: OpenApiResponse(BriefUserDisplaySerializer(many=True), "Success"),
            404: OpenApiResponse(ErrorSerializer, "User not found")
        }
    )
    def list(self, request, *args, **kwargs):
        """Returns all users"""

        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={
            204: OpenApiResponse(OpenApiTypes.NONE, "Successful, no content"),
            404: OpenApiResponse(ErrorSerializer, "User not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a user"""

        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser])
    def delete_all(self, request, *args, **kwargs):
        """Convenience method to delete all users"""

        q_set = self.get_queryset()
        q_set.delete()
        return Response({"message": "All users sucessfully deleted."})

    @extend_schema(
        parameters=[*paginator_header_params],
        responses={
            200: OpenApiResponse(
                BriefUserDisplaySerializer(many=True),
                "Successful, shows new list of user's friends."
            ),
            400: OpenApiResponse(ValidationErrorSerializer, "Bad request"),
            404: OpenApiResponse(ErrorSerializer, "User not found")
        }
    )
    @action(["post"], detail=True, serializer_class=AddFriendsSerializer)
    def add_friends(self, request, *args, **kwargs):
        """Add other users as freinds"""

        ser = self.get_serializer(data=request.data)
        if ser.is_valid():
            friends_qset = ser.save()
            data = BriefUserDisplaySerializer(friends_qset, many=True).data
            return Response(data)
        else:
            return ValidationErrorSerializer(data=ser.errors).json_response()

    @extend_schema(
        parameters=[*paginator_header_params],
        responses={
            200: OpenApiResponse(
                OnlineUserDisplaySerializer(many=True),
                "Successful, shows all user's friends."
            ),
            404: OpenApiResponse(ErrorSerializer, "User not found")
        }
    )
    @action(["get"], detail=True, serializer_class=OnlineUserDisplaySerializer)
    def friends(self, request, *args, **kwargs):
        """View list of user's friends"""

        user = request.user
        friends_qset = user.friends.all()
        data = self.get_serializer(friends_qset, many=True).data
        return Response(data)

    @extend_schema(
        parameters=[*paginator_header_params],
        responses={
            200: OpenApiResponse(
                BriefUserDisplaySerializer(many=True),
                "Successful, shows search results."
            ),
            400: OpenApiResponse(
                URLParamsValidationErrorSerializer,
                "Bad URL parmams format."
            ),
            404: OpenApiResponse(ErrorSerializer, "User not found")
        }
    )
    @action(["get"], detail=True, serializer_class=SearchUrlParamsSerializer)
    def search(self, request, *args, **kwargs):
        """
        Search for user's friends using first name or last name.
        Search is based case-insensitive text matches, nothing fancy.
        """
        query_params = dict(request.query_params)
        ser = self.get_serializer(data=query_params)
        if ser.is_valid():
            search_qset = ser.get_query()
            data = BriefUserDisplaySerializer(search_qset, many=True).data
            return Response(data)
        else:
            return URLParamsValidationErrorSerializer(data=ser.errors).json_response()

    @extend_schema(
        responses={
            204: OpenApiResponse(OpenApiTypes.NONE, "Successful, no content"),
            400: OpenApiResponse(ValidationErrorSerializer, "Bad request"),
            404: OpenApiResponse(ErrorSerializer, "User not found"),
            405: OpenApiResponse(None, "Wrong online status policy")
        }
    )
    @action(
        ["post"], detail=True, serializer_class=UIOpenSerializer,
        authentication_classes=[JWTAuthentication]
    )
    def ui_online_status(self, request, *args, **kwargs):
        """
        Sets online status if UI is in focus or not. Frontend is
        expected to call this method when app UI is in focus or open.
        Method only allowed if ONLINE_STATUS_POLICY is UIOpenIsOnline. 
        """

        if app_settings["ONLINE_STATUS_POLICY"] != "UIOpenIsOnline":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        ser = self.get_serializer(data=request.data)
        if ser.is_valid():
            ui_open: bool = ser.validated_data["ui_open"]
            user, token = request.user, request.auth
            UIOpenIsOnline(user, token).set_online_status(online=ui_open)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return ValidationErrorSerializer(data=ser.errors).json_response()

    def get_serializer(self, *args, **kwargs):
        if (self.action == "list"):
            return BriefUserDisplaySerializer(*args, **kwargs)
        elif (self.action == "retrieve"):
            return UserDisplaySerializer(*args, **kwargs)
        else:
            return super().get_serializer(*args, **kwargs)

