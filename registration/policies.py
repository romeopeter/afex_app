"""
This module captures all policies adopted by registration app.
"""
from abc import ABC, abstractmethod
from datetime import timedelta

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.utils import datetime_from_epoch

from django.utils import timezone

from common_app.utils.general_utils import RedisTimePersist


class BaseOnlinePolicyABC(ABC):

    @abstractmethod
    def set_key(self):
        pass


class BaseOnlinePolicy(BaseOnlinePolicyABC):
    def __init__(self, user, validated_token: Token = None):
        self.token = validated_token
        self.user = user
        if validated_token is not None:
            self.ttl = self.get_time_delta(self.token)
        self.redis = RedisTimePersist()

    def __bool__(self):
        return self._is_online()

    def get_time_delta(self, token):
        exp_datetime = datetime_from_epoch(token["exp"])
        delta = exp_datetime - timezone.now()
        return delta.seconds


class LoggedInIsOnline(BaseOnlinePolicy):
    """User is online when logged in."""

    def set_key(self):
        self.redis.hset(
            name=self.user.id, key="logged_in", value=1,
            ttl=self.ttl
        )

    def _is_online(self) -> bool:
        ttl = self.redis.time_to_live(self.user.id)
        return ttl > 0


class UIOpenIsOnline(BaseOnlinePolicy):
    """User is online when application UI is open/in focus."""
    
    def set_key(self):
        self.redis.hset(
            name=self.user.id, key="logged_in", value=1,
            other_kv={"ui_open": 1}, ttl=self.ttl
        )

    def _is_online(self) -> bool:
        name = self.user.id
        ttl = self.redis.time_to_live(name)
        if ttl > 0 and self.redis.hget(name, "ui_open"):
            return True
        else:
            return False

    def set_online_status(self, *, online=True) -> None:
        self.redis.hset(
            name=self.user.id, key="logged_in", value=1,
            other_kv={"ui_open": 1 if online else 0}, ttl=self.ttl
        )

        



