from django.core.exceptions import ValidationError
from django.dispatch import receiver

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field, OpenApiTypes

from common_app.mixins.serializer_mixins import DisplaySerializerMixin

from .models import Chat



class ChatGenericSerializer(serializers.ModelSerializer):

    nullable_fields = ["message", "location"]
    req_fields = ["sender", "receiver"]


    def validate(self, attrs):
        super().validate(attrs)

        # validate that they are friends
        initiator = attrs["sender"]
        receiver = attrs["receiver"]
        if not initiator.is_friends_with(receiver):
            raise ValidationError(
                "Only friends can send chat messages to eachother",
                "non_friends"
            )

        message = attrs.get("message")
        location = attrs.get("location")
        file = attrs.get("file")

        # validate that some information is passed
        if message is None and location is None and file is None:
            raise ValidationError(
                "A message or location or file is required.",
                "no_information"
            )
        
        return attrs

    class Meta:
        model = Chat
        fields = "__all__"


class ChatCreateSerializer(ChatGenericSerializer):

    class Meta(ChatGenericSerializer.Meta):
        extra_kwargs = {
            "receiver": {"required": True}
        }

class ChatDisplaySerializer(DisplaySerializerMixin, ChatGenericSerializer):

    sender = serializers.SerializerMethodField(
        help_text="Initator of this chat"
    )

    receiver = serializers.SerializerMethodField(
        help_text="The receiver of this chat"
    )

    @extend_schema_field(OpenApiTypes.STR)
    def get_sender(self, instance):
        return instance.sender.get_full_name()

    @extend_schema_field(OpenApiTypes.STR)
    def get_receiver(self, instance):
        return instance.receiver.get_full_name()

    