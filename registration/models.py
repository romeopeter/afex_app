from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver

from .managers import UserManager
from .authentication import get_online_policy_class

# from chats.models import Chat




class User(AbstractUser):

    # model fields
    email = models.EmailField(unique=True, help_text="Email of user")

    first_name = models.CharField(
        max_length=150,
        help_text="First name of user"
    )

    last_name = models.CharField(
        max_length=150,
        help_text="Last name of user"
    )

    friends = models.ManyToManyField(
        "self",
        help_text="Friends of the user"
    )

    # other class constants
    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # manager
    objects = UserManager()

    def is_online(self):
        online_policy = get_online_policy_class()(self)
        return bool(online_policy)

    def is_friends_with(self, other_user):
        return bool(self.friends.filter(pk=other_user.id))




