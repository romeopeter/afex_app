from django.apps import AppConfig
from registration.authentication import CustomAuthBackendSchema


class RegistrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'registration'

    def ready(self):
        CustomAuthBackendSchema
