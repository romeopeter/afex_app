from django.db import models

from django.contrib.auth import get_user_model
from common_app.models import BaseModel

from .managers import ChatManager
from afex_app.storage_backends import MediaStorage

from django.core.files.storage import DefaultStorage

class Chat(BaseModel):

    sender = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        related_name="chats_sent",
        help_text="The initiator of this chat."
    )

    receiver = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, null=True,
        related_name="chats_received",
        help_text="The receiver of this chat."
    )

    respond_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="responses",
        help_text="Chat ID you want to respond to"
    )

    message = models.TextField(
        max_length=500, null=True,
        help_text="Chat message"
    )

    location = models.URLField(
        null=True,
        help_text="A location url"
    )

    file = models.FileField(
        null=True,
        help_text="A file you wish to upload"
    )

    objects = ChatManager()


