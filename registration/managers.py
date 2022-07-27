from django.contrib.auth.models import BaseUserManager
from common_app.mixins.manager_mixins import ModelManagerMixin


class UserManager(ModelManagerMixin, BaseUserManager):

    def get_queryset(self):
        return super().get_queryset().order_by("first_name")

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create(self, email=None, password=None, **extra_fields):
        if email is None or password is None:
            raise ValueError("'email' and 'password' are required fields")
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def get_active_user(self, **kwargs):
        if "is_active" not in kwargs:
            kwargs["is_active"] = True
        return self.get(**kwargs)

    def get_active_user_or_none(self, **kwargs):
        if "is_active" not in kwargs:
            kwargs["is_active"] = True
        return self.get_or_none(**kwargs)

        


