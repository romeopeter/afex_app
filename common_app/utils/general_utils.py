import os

import redis
from decouple import config
from typing import Optional, Union, Any

from django.conf import settings

app_settings: dict = settings.APPLICATION_SETTINGS


def env_is_dev() -> bool:
    return os.environ.get("DJANGO_SETTINGS_MODULE") == "afex_app.settings.development"

def env_is_prod() -> bool:
    return os.environ.get("DJANGO_SETTINGS_MODULE") == "afex_app.settings.production"


class CastAs:
    """Utility to cast bytes to other types"""

    string = lambda v: v if v is None else str(v, encoding="utf-8")
    bool = lambda v: v if v is None else bool(int(v))
    int = lambda v: v if v is None else int(v)


class RedisTimePersist:
    """Class to handle Redis actions"""

    def __init__(self, ttl=None) -> None:
        self.ttl = ttl or app_settings["DEFAULT_PIN_TTL"]

        if env_is_dev():    # local
            self.instance = redis.StrictRedis(
                host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0
            )
        else:   # production
            self.instance = redis.from_url(config("REDIS_URL"))

    def set(self, key: str, value: str) -> None:
        self.instance.set(key, value, ex=self.ttl)

    def get(self, key, cast=CastAs.string) -> Optional[Any]:
        value: Optional[bytes] = self.instance.get(key)
        return cast(value)
    
    def hset(self, name, key, value, other_kv: dict = None, ttl: Optional[int] = None) -> None:
        self.instance.hset(name, key, value, other_kv)
        if ttl is not None:
            self.instance.expire(name, ttl)

    def hget(self, name, key, cast=CastAs.bool) -> Optional[Any]:
        value: Optional[bytes]= self.instance.hget(name, key)
        return cast(value)

    def time_to_live(self, key) -> int:
        t = self.instance.ttl(key)
        return t


