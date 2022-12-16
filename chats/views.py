from django.db.models import Q
from django.dispatch import receiver

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (
    extend_schema, OpenApiResponse, OpenApiTypes
)

from common_app.serializers import ValidationErrorSerializer
from common_app.pagination import GeneralPagingation

from exceptions_and_logging.serializers import ErrorSerializer

from .models import Chat
from .serializers import ChatCreateSerializer, ChatDisplaySerializer

class ChatViewset(
    ListModelMixin, DestroyModelMixin, CreateModelMixin, GenericViewSet
):

    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChatDisplaySerializer
    pagination_class = GeneralPagingation

    @extend_schema(
        responses={
            201: OpenApiResponse(
                ChatDisplaySerializer, "Successfully created a chat."
            ),
            400: OpenApiResponse(
                ValidationErrorSerializer, "Bad request"
            )
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a chat between the logged in user and another user"""

        user = request.user
        data = request.data.copy()
        data["sender"] = user.id
        ser = ChatCreateSerializer(data=data)
        if ser.is_valid():
            chat = ser.save()
            data = ChatDisplaySerializer(chat).data
            return Response(data, status.HTTP_201_CREATED)
        else:
            return ValidationErrorSerializer(data=ser.errors).json_response()

    @extend_schema(
        responses={
            204: OpenApiResponse(OpenApiTypes.NONE, "Successful, no content"),
            404: OpenApiResponse(ErrorSerializer, "User not found")
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a chat"""

        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                ChatDisplaySerializer(many=True),
                "Successfully retrieved all chats for this user."
            ),
        }
    )
    def list(self, request, *args, **kwargs):
        """List chats that belong to the logged in user."""

        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        from_user = Q(sender=user)
        to_user = Q(receiver=user)
        return super().get_queryset().filter(from_user | to_user)



