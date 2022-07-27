from django.core.exceptions import ValidationError

class TextMatches:

    def __init__(self, text: str) -> None:
        self.text = text

    def __call__(self, value) -> None:
        if not str(value) == self.text:
            raise ValidationError(
                "Text mismatch", "mismatch"
            )