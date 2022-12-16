from .base import *

# DEBUG = True

ALLOWED_HOSTS = ["*"]

if config("DB_IS_DEFAULT", cast=bool):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("LOCAL_DB_NAME"),
            "USER": config("LOCAL_DB_USER"),
            "PASSWORD": config("LOCAL_DB_PASSWORD"),
            "HOST": "localhost",
            "PORT": "5432",
        }
    }
