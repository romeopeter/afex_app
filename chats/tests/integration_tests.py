import json
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

from ..models import Chat




# @override_settings(EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend')
class TestViews(TestUtilsMixin, TestCase):

    def setUp(self) -> None:
        self.client = Client()

    
    def test_user_viewsets(self):
        url = "/v1/chats/"
        user_1 = self.create_user(email="friend@one.com")
        user_2 = self.create_user(email="friend@two.com")
        # user_3 = self.create_user(email="friend@three.com")

        create_params = {
            "sender": user_1.id, "receiver": user_2.id,
        }

        self.authenticate(user_1)
        self.headers.pop("content_type")
        
        # test failure, validation error - not friends (400)
        resp = self.client.post(url, create_params, **self.headers)
        self.assertEqual(resp.status_code, 400)

        # test failure, validation erro - no information (400)
        user_1.friends.add(user_2)
        resp = self.client.post(url, create_params, **self.headers)
        self.assertEqual(resp.status_code, 400)

        # test success, create (201)
        message = "How are you today?"
        create_params["message"] = message
        with open("chats/tests/a_file.txt") as my_file:
            create_params["file"] = my_file
            resp = self.client.post(url, create_params, **self.headers)
            self.assertEqual(resp.status_code, 201)

        # test success, create with chatID (201)
        chat_id = resp.json()["id"]
        create_params = {
            "sender": user_2.id, "receiver": user_1.id,
            "message": "I am fine, thank you", "respond_to": chat_id 
        }
        self.authenticate(user_2)
        resp = self.client.post(url, create_params, **self.headers)
        chat_id_2 = resp.json()["id"]
        chat_2 = Chat.objects.get(pk=chat_id_2)
        self.assertEqual(resp.status_code, 201)

        # test faliure, create with missing chat ID not found (400)
        create_params["respond_to"] = chat_id + 99
        resp = self.client.post(url, create_params, **self.headers)
        self.assertEqual(resp.status_code, 400)

        # test success, list (200)
        create_params = {
            "sender": user_1, "receiver": user_2,
            "message": "Abeg I need urgent 2k", "respond_to": chat_2
        }
        Chat.objects.create(**create_params)
        self.authenticate(user_1)
        resp = self.client.get(url, **self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 3)





