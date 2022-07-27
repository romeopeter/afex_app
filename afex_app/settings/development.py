from .base_settings import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('LOCAL_DB_NAME'),
        'USER': config('LOCAL_DB_USER'),
        'PASSWORD': config('LOCAL_DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}