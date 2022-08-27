import random

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken

from common_app.utils.general_utils import RedisTimePersist

from .tasks import task_send_confirmation_pin_email



def get_pin_confirmation_url(user, domain):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    url = reverse("pin_confirm_account", kwargs={"uidb64": uidb64})
    return f"https://{domain}{url}"

def generate_pin(length: int = 4):
    digit_seq: list = (random.sample(range(0, 9), length))
    return "".join([str(d) for d in digit_seq])

def confirm_user_and_return_tokens(user) -> dict:
    user.is_active = True
    user.confirmed_at = timezone.now()
    user.save()
    refresh = RefreshToken.for_user(user)
    access = RefreshToken(str(refresh)).access_token
    data = {
        "refresh": str(refresh), "access": str(access)
    }
    return data


class SignUpWithPin:
    """
    Sign Up strategy used for this application.
    """

    def __init__(self, serializer, admin=False) -> None:
        self.serializer = serializer
        self.admin = False

    def sign_up(self):
        # generate confirmation pin
        confirmation_pin = generate_pin()

        # save user
        user = self.serializer.save()

        # persist short lived pin
        RedisTimePersist().set(
            f"sign_up_confirmation_pin_{user.id}",
            confirmation_pin
        )
        
        # set confirmation pin on serializer
        self.serializer.confirmation_pin = confirmation_pin

        # NOTE: We will ignore this step. Reason is we will be sending the PIN
        # via API to the user for the scope of this app. Ideally, this should be
        # sent to the user via email.
        # Change email settings to SMTP backend and provide valid email credentials then
        # uncomment the code below to use it.

        # send confirmation pin email
        # task_send_confirmation_pin_email(
        #     first_name=user.first_name, confirmation_pin=confirmation_pin,
        #     email=user.email
        # )

    @property
    def data(self):
        return self.serializer.data

