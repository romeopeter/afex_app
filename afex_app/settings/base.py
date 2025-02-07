"""
Django settings for afex_app project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
from decouple import config, Csv
from datetime import timedelta
import os

# set base dir to root folder
BASE_DIR = Path(__file__).resolve().parents[2]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# Production secret key
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    "django_extensions",
    "storages",
    # project apps
    "common_app",
    "exceptions_and_logging",
    "registration",
    "chats",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "afex_app.versioned_urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "afex_app.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Lagos"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# AWS settings
USE_S3 = config("USE_S3", default=False, cast=bool)
if USE_S3:
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME")
    AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    DEFAULT_FILE_STORAGE = "afex_app.storage_backends.MediaStorage"
    STATICFILES_STORAGE = "afex_app.storage_backends.StaticStorage"
else:
    STATIC_URL = "/static/"
    STATICFILES_DIRS = [BASE_DIR / "static"]
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "registration.User"

# Rest Framework Settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # "rest_framework.authentication.BasicAuthentication",
        "registration.authentication.CustomAuthBackend",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "exceptions_and_logging.exc_handler.app_exception_handler",
}

env = os.environ.get("DJANGO_SETTINGS_MODULE")
dev = "afex_app.settings.development"

# Simple JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7) if env == dev else timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(weeks=2) if env == dev else timedelta(weeks=1),
}

# Cors settings, experimental app - allow all for productiom and development
CORS_ALLOW_ALL_ORIGINS = True

# Email settings, use console backend for productiom and development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Exceptions and Logging settings
EXC_EMAIL_RECEPIENTS = ["chidinnamekannadi@gmail.com"]
EXC_SENDER_EMAIL = "errors@afex_app.com"
EXC_USERNAME_FIELD = "email"

# Spectacular Settings
SPECTACULAR_SETTINGS = {
    "TITLE": "Afex Social Media API",
    "DESCRIPTION": "API endpoints for handling request for/ Afex social media app.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_URLCONF": "afex_app.versioned_urls",
    "SERVERS": [] if env == dev else [{"url": "https://afex-app.herokuapp.com"}],
    "SWAGGER_UI_SETTINGS": {
        "url": "/v1/schema/",  # relative path
    },
}

# Settings unique to this application
APPLICATION_SETTINGS = {
    # Default time to live before pins/keys are expired.
    "DEFAULT_PIN_TTL": timedelta(hours=1),
    "ONLINE_STATUS_POLICY": config("ONLINE_STATUS_POLICY", default="LoggedInIsOnline"),
}
