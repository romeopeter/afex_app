import time
from decouple import config


from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from common_app.serializers import ValidationErrorSerializer, URLParamsValidationErrorSerializer
from common_app.utils.test_utils import TestUtilsMixin
from common_app.utils.general_utils import app_settings

from exceptions_and_logging.serializers import ErrorSerializer

from ..serializers import IntegrityErrorSerializer
from ..serializers import SignInSerializer
from ..policies import UIOpenIsOnline


# @override_settings(EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend')
class TestViews(TestUtilsMixin, TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.headers = {}
        self.email, self.password = "chidi@gmail.com", "password"
        return super().setUp()

    def _create_user(self, **create_user_params):
        sign_up_params = {
            "first_name": "Chidi", "last_name": "Nnadi"
        }
        email = create_user_params.pop("email", self.email)
        password = create_user_params.pop("password", self.password)
        sign_up_params.update(create_user_params)
        
        return get_user_model().objects.create(email, password, **sign_up_params)

    def test_sign_up(self):
        # app_settings["SIGN_UP_AUTH_TYPE"] = "pin"
        url = "/v1/registration/sign_up/"

        sign_up_params = {
            "email": self.email, "password": self.password,
            "confirm_password": self.password, "first_name": "Chidi",
            "last_name": "Nnadi",
        }

        # test success, create (201)
        resp = self.client.post(url, sign_up_params)
        self.assertEqual(resp.status_code, 201)

        # test failure, conflict (409)
        resp = self.client.post(url, sign_up_params)
        self.assertTrue(IntegrityErrorSerializer(data=resp.json()).is_valid())
        self.assertTrue(resp.status_code == 409)

        # test failure, bad request (400) - non field errors
        sign_up_params["confirm_password"] = "wrong password"
        sign_up_params["email"] = "new@email.com"
        resp = self.client.post(url, sign_up_params)
        self.assertTrue(ValidationErrorSerializer(data=resp.json()).is_valid())
        self.assertTrue(resp.status_code, 400)

        # test failure, bad request (400) - field errors
        sign_up_params["confirm_password"] = self.password
        sign_up_params["email"] = "wrong_email_format"
        resp = self.client.post(url, sign_up_params)
        self.assertTrue(ValidationErrorSerializer(data=resp.json()).is_valid())
        self.assertTrue(resp.status_code, 400)

    def test_sign_in(self):

        # test success, (200)
        user = self._create_user(is_active=True)
        sign_in_params = {"email": self.email, "password": self.password}
        resp = self.client.post("/v1/registration/sign_in/", sign_in_params)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(SignInSerializer(data=resp.json()).is_valid())

        # test failure, unauthorized - wrong email (401)
        sign_in_params["email"] = "wrong email"
        resp = self.client.post("/v1/registration/sign_in/", sign_in_params)
        self.assertEqual(resp.status_code, 401)
        # print(json.dumps(resp.json(), indent=4))
        self.assertTrue(ErrorSerializer(data=resp.json()).is_valid())

    def test_token_refresh(self):
        # test token refresh view, test success (200)
        refresh_token = str(RefreshToken())
        resp = self.client.post("/v1/token/refresh/", {"refresh": refresh_token})
        self.assertEqual(resp.status_code, 200)

        # test wrong token (401)
        resp = self.client.post("/v1/token/refresh/", {"refresh": "invalid token"})
        self.assertEqual(resp.status_code, 401)

    def test_user_viewsets(self):
        # test success, get (200)
        user = self.create_user(email="john@doe.com", is_active=True)
        self.authenticate(user)
        resp = self.client.get(f"/v1/users/{user.id}/", **self.headers)
        self.assertEqual(resp.status_code, 200)

        # test success, list (200)
        resp = self.client.get("/v1/users/", **self.headers)
        self.assertTrue(status.is_success(resp.status_code))

        # test success, retrieve (200)
        resp = self.client.get(f"/v1/users/{user.id}/", **self.headers)
        self.assertTrue(status.is_success(resp.status_code))

        # test success, delete (204)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        resp = self.client.delete(f"/v1/users/{user.id}/", **self.headers)
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(get_user_model().objects.all().count(), 0)

        # test success, delete all (204)
        user = self.create_user(email="admin@user.com", is_staff=True, is_active=True)
        self.authenticate(user)
        self.create_user(email="email1@gmail.com")
        self.create_user(email="email2@gmail.com")

        resp = self.client.delete(f"/v1/users/delete_all/", **self.headers)
        self.assertTrue(status.is_success(resp.status_code))

    def test_add_friends(self):
        user = self.create_user(email="john@doe.com", is_active=True)
        friend_1 = self.create_user(email="friend@one.com", is_active=True)
        friend_2 = self.create_user(email="friend@two.com", is_active=True)
        friend_3 = self.create_user(email="friend@three.com", is_active=True)

        post_params = {
            "friends": [friend_1.id, friend_2.id]
        }

        url = f"/v1/users/{user.id}/add_friends/"
        self.authenticate(user)

        # test success, add friend (200)
        resp = self.client.post(url, post_params, **self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), len(user.friends.all()))

        # test failure, bad requests (400)
        post_params["friends"] = [friend_1.email, friend_2.email]
        resp = self.client.post(url, post_params, **self.headers)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(ValidationErrorSerializer(data=resp.json()).is_valid())

    def test_show_friends(self):
        user = self.create_user(email="john@doe.com", is_active=True)
        # create friends
        self.create_user(email="friend@one.com", is_active=True)
        self.create_user(email="friend@two.com", is_active=True)
        self.create_user(email="friend@three.com", is_active=True)
        # add friends
        friends_qset = get_user_model().objects.exclude(pk=user.id)
        user.friends.set(friends_qset)

        url = f"/v1/users/{user.id}/friends/"
        self.authenticate(user)
        # test success, 200
        resp = self.client.get(url, **self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 3)

    def test_search(self):
        user = self.create_user(email="john@doe.com", is_active=True)
        # create friends
        self.create_user(email="friend@one.com", first_name="Lucas", is_active=True)
        self.create_user(email="friend@two.com", last_name="franklucas", is_active=True)
        self.create_user(email="friend@three.com", first_name="Frank", is_active=True)

        # test success, case-insensitive search in first_name or last_name (200)
        # example 1
        url = f"/v1/users/{user.id}/search/?name=lucas"
        self.authenticate(user)
        resp = self.client.get(url, **self.headers)
        self.assertEqual(resp.status_code, 200)
        # print(resp.json())
        self.assertEqual(len(resp.json()), 2)
        # example 2
        url = f"/v1/users/{user.id}/search/?name=frank"
        resp = self.client.get(url, **self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)
        # example 3 (no hits)
        url = f"/v1/users/{user.id}/search/?name=no_hits"
        resp = self.client.get(url, **self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 0)

        # test failure, bad url params (400)
        url = f"/v1/users/{user.id}/search/?wrong_name=no_hits"
        resp = self.client.get(url, **self.headers)
        self.assertEqual(resp.status_code, 400)
        # assert response is properly formatted
        self.assertTrue(URLParamsValidationErrorSerializer(data=resp.json()).is_valid())

    def test_LoggedInIsOnline(self):
        # create user
        app_settings["ONLINE_STATUS_POLICY"] = "LoggedInIsOnline"
        user = self.create_user(email="john@doe.com")
        self.authenticate(user)
        # test success, user online (200)
        resp = self.client.get(f"/v1/users/{user.id}/", **self.headers)
        self.assertTrue(user.is_online())

        # create friend
        friend_1 = self.create_user(email="friend@one.com")
        self.authenticate(friend_1, exp=2)
        # persit exp in redis
        resp = self.client.get(f"/v1/users/{friend_1.id}/", **self.headers)
        # assert user is online
        self.assertTrue(friend_1.is_online())
        # expire key
        time.sleep(3)
        # assert user is not online
        self.assertFalse(friend_1.is_online())
        # add other friend 
        friend_2 = self.create_user(email="friend@two.com")
        self.authenticate(friend_2)
        # persit exp in redis
        resp = self.client.get(f"/v1/users/{friend_1.id}/", **self.headers)
        # add freinds to user
        user.friends.add(friend_1)
        user.friends.add(friend_2)
        # show user's friends
        url = f"/v1/users/{user.id}/friends/"
        self.authenticate(user)
        resp = self.client.get(url, **self.headers)
        self.assertFalse(resp.json()[0]["online"])
        self.assertTrue(resp.json()[1]["online"])
        self.assertEqual(resp.status_code, 200)

    def test_UIOpenIsOnline(self):
        # create user
        app_settings["ONLINE_STATUS_POLICY"] = "UIOpenIsOnline"
        user = self.create_user(email="john@doe.com")
        self.authenticate(user)
        # asssrt user is online
        resp = self.client.get(f"/v1/users/{user.id}/", **self.headers)
        self.assertTrue(user.is_online())

        # test user is not online after UI is closed
        data = {"ui_open": False}
        url = f"/v1/users/{user.id}/ui_online_status/"
        # change online status
        resp = self.client.post(url, data, **self.headers)
        self.assertEqual(resp.status_code, 204)
        # asssrt user is offline
        self.assertFalse(bool(UIOpenIsOnline(user)))









        


        



        








        
        



