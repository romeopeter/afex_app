import json
from typing import List, Tuple, Union
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class TestUtilsMixin:

    def create_groups(self, groups: List[str]):
        """Create user groups"""

        for name in groups:
            Group.objects.create(name=name)

    def create_perms(self, perms: Tuple[Tuple[str, str]], model=None):
        """Create permissions
        
        Parameters
        ----------
        perms: Tuple[Tuple[str, str]]
            An iterable of a fixed two length tuple representing
            permission name and codename respectively
        model: Optional[models.Model]
            Defaults to user model if no model is given.
        """

        model = model or get_user_model()
        ct_user = ContentType.objects.get_for_model(model)
        for tup in perms:
            it = iter(tup)
            name = next(it)
            codename = next(it)
            Permission.objects.create(
                name=name, codename=codename, content_type=ct_user
            )

    def create_user(self, **create_user_params):
        """
        Requires only email to create a user, fills in the rest.
        It will create random phone numbers if a clash occurs.
        """

        email = create_user_params.pop("email", None)
        password = create_user_params.pop("password", None)
        groups = create_user_params.pop("groups", None)
        confirm = create_user_params.pop("confirm", False)

        if email is None and not hasattr(self, "email"):
            raise AssertionError("Requires an email in the params or in the instance")
        email = email or self.email

        if password is None:
            password = getattr(self, "password", None) or "random_password"

        sign_up_params = {
            "first_name": "John", "last_name": "Doe",
        }

        sign_up_params.update(create_user_params)
        
        user = get_user_model().objects.create(email, password, **sign_up_params)

        if groups is not None:
            if not isinstance(groups, (list, tuple)):
                raise AssertionError("Groups must be an Iterable.")

            for name in groups:
                grp, _ = Group.objects.get_or_create(name=name)
                user.groups.add(grp)

        return user

    def authenticate(self, user, exp: int = None):
        """Sets self.header to contain bearer access token for user"""

        headers = getattr(self, "headers", None)
        if headers is None or not headers:
            headers = {'content_type': "application/json"}

        if exp is None:
            access_token = str(RefreshToken().for_user(user).access_token)
        else:
            token = AccessToken().for_user(user)
            token.set_exp(lifetime=timedelta(seconds=exp))
            access_token = str(token)

        headers.update({"HTTP_AUTHORIZATION": 'Bearer ' + access_token})
        self.headers = headers
