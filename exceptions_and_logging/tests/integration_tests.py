from django.test import TestCase, Client, override_settings

from ..serializers import ErrorSerializer


# @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
class TestViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()

    # prepend with 'test'
    def non_drf_view(self):
        url = "/exc-and-logging/drf/%s/"
        message = "exceptions and logging is dope."
        # test success, python errors
        resp = self.client.post(
            url % "python", {"message": message},
            content_type="application/json"
        )
        self.assertTrue(ErrorSerializer(data=resp.data).is_valid())

        # test success, regular DRF errors
        resp = self.client.post(
            url % "drf_regular", {"message": message},
            content_type="application/json"
        )
        self.assertTrue(ErrorSerializer(data=resp.data).is_valid())

        # test success, DRF Validation errors
        resp = self.client.post(
            url % "drf_validation", {"message": message},
            content_type="application/json"
        )
        self.assertTrue(ErrorSerializer(data=resp.data).is_valid())

        # test success, Exc and Logging errors
        resp = self.client.post(
            url % "exc_and_log", {"message": message},
            content_type="application/json"
        )
        self.assertTrue(ErrorSerializer(data=resp.data).is_valid())

