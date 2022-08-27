from django.test import SimpleTestCase

from ..utils import generate_pin


class TestUtils(SimpleTestCase):

    def test_four_digit_pin(self):
        self.assertTrue(len(generate_pin()) == 4)


