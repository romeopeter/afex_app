from .base import *
import dj_database_url

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

MIDDLEWARE += [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# AWS settings
STATIC_URL = "/static/"

if not DEBUG:
    STATICFILES_DIRS = [BASE_DIR / "static"]
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    # MEDIA_URL = "/media/"
    # MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DATABASES = {
    'default': dj_database_url.config(config("RENDER_DATABASE_URL"), conn_max_age=600)
}