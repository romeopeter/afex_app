from typing import List
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


from drf_spectacular.utils import extend_schema_field, OpenApiTypes

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework import status
from rest_framework.response import Response as DRFResponse

from drf_spectacular.utils import extend_schema_field

from common_app.mixins.serializer_mixins import (
    DisplaySerializerMixin, URLParamsSerializerMixin
)
from common_app.validators import TextMatches


from .messages.error_messages import (
    PASSWORD_MISSMATCH, DUPLICATE_EMAIL,
)


app_settings = settings.APPLICATION_SETTINGS
read_only = {"read_only": True}
user_qset = get_user_model().objects.all()


class OnlineSerializer(serializers.Serializer):
    online = serializers.SerializerMethodField(
        help_text="Indicates if a user is online or not."
    )

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_online(self, instance):
        return instance.is_online()


class UserGenericSerializer(serializers.ModelSerializer):
    """Bare bones user serializer"""

    class Meta:
        model = get_user_model()
        fields = "__all__"
        extra_kwargs = {
            "friends": read_only
        }

class BriefUserDisplaySerializer(DisplaySerializerMixin, UserGenericSerializer):
    """User display serializer that shows limited user information"""

    class Meta(UserGenericSerializer.Meta):
        fields = ["id", "first_name", "last_name"]


class OnlineUserDisplaySerializer(DisplaySerializerMixin, OnlineSerializer, UserGenericSerializer):
    """User display serializer that shows limited user information and online status"""

    class Meta(UserGenericSerializer.Meta):
        fields = ["id", "first_name", "last_name", "online"]


class UserDisplaySerializer(DisplaySerializerMixin, UserGenericSerializer):
    """User serializer for display"""

    # Overriden to disable unique constraint checker
    email = serializers.EmailField()
    friends = BriefUserDisplaySerializer(many=True)

    class Meta(UserGenericSerializer.Meta):
        fields = None
        exclude = ["password"]


class SignUpSerializer(UserGenericSerializer):
    """Serializer for sign up logic"""

    # class fields
    email = serializers.EmailField(
        validators=[UniqueValidator(user_qset, DUPLICATE_EMAIL)],
        help_text="Email of user"
    )
    password = serializers.CharField(
        write_only=True, help_text="User password"
    )

    confirm_password = serializers.CharField(
        write_only=True, help_text="Password to confirm"
    )

    def validate(self, attrs):
        # validate password
        if attrs["password"] != attrs["confirm_password"]:
            raise ValidationError(PASSWORD_MISSMATCH, "password_missmatch")
        attrs.pop("confirm_password")
        return attrs

    def create(self, validated_data):
        # set user as active
        validated_data.update({"is_active": True})
        return get_user_model().objects.create(**validated_data)

    class Meta(UserGenericSerializer.Meta):
        extra_kwargs = {
            # "first_name": {"required": True}, "last_name": {"required": True},
            "groups": read_only, "user_permissions": read_only,
            "is_active": read_only, "date_joined": read_only, "is_superuser": read_only,
            "confirmed_at": read_only, "last_login": read_only,
            "is_staff": read_only, "friends": read_only
        }


class TokenResponseSerializer(serializers.Serializer):
    """Displays access and refresh tokens."""

    access = serializers.CharField()
    refresh = serializers.CharField(required=False)


class SignInSerializer(serializers.Serializer):
    """Serializer for sign in"""

    user = UserDisplaySerializer()
    tokens = TokenResponseSerializer()

class AddFriendsSerializer(serializers.Serializer):
    friends = serializers.ListSerializer(
        child=serializers.IntegerField(),
        help_text="User ID's of friends to add."
    )

    def create(self, validated_data: dict) -> models.QuerySet:
        # remove_duplicates
        user = self.get_user()
        friend_ids = set(validated_data["friends"])
        friends_qset = get_user_model().objects \
            .filter(id__in=friend_ids) \
            .exclude(id=user.id)
        for friend in friends_qset:
            user.friends.add(friend)
        return user.friends.all()

    def get_user(self):
        return self.context["request"].user


class SearchUrlParamsSerializer(serializers.Serializer):
    """Serializes URL params for friends search"""

    name = serializers.ListSerializer(
        child=serializers.CharField(), max_length=1,
        help_text=(
            "First or last name of friend to search for. "
            "Search is based on text matches, nothing fancy."
        )
    )

    def validate_name(self, name_list: List[str]):
        return name_list[0]

    def get_user(self):
        return self.context["request"].user 

    def get_query(self) -> models.QuerySet:
        name = self.validated_data["name"]
        view = self.context["view"]
        user = self.get_user()
        users_qset = view.get_queryset().exclude(pk=user.id)
        in_first_name = models.Q(first_name__icontains=name)
        in_last_name = models.Q(last_name__icontains=name)
        final_qset = users_qset.filter(in_first_name | in_last_name)
        return final_qset


class UIOpenSerializer(serializers.Serializer):
    ui_open = serializers.BooleanField(
        help_text="Indicates if application UI is in focus."
    )
        

class IntegrityErrorSerializer(serializers.Serializer):
    """Hack for isolating Integrity errors from general validation errors."""
    
    http_status_code = status.HTTP_409_CONFLICT

    email = serializers.ListSerializer(
        child=serializers.CharField(
            validators=[TextMatches(DUPLICATE_EMAIL)]
        ), required=False,
        help_text="users with this email already exists."
    )

    def validate(self, attrs):
        # make sure at least one parameter is given
        if not attrs:
            raise ValidationError(
                "Data cannot be empty."
            )
        return attrs

    def _is_valid(self):
        """Return self instead of True so object can be reused"""

        return self if self.is_valid() else False

    def http_response_409(self) -> DRFResponse:
        return DRFResponse(self.data, self.http_status_code)
