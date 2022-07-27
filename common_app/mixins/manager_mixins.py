"""Manager functionalities common to apps"""

from typing import Optional

from django.db import models


class ModelManagerMixin:
    """Extra functionalities for app model managers"""

    def get_or_none(self, **kwargs) -> Optional[models.Model]:
        """Get an Object or return None
        
        You're most likely not interested in the reason why this query
        failed, you just want to know if a value was returned or not.
        """

        try:
            obj = self.get(**kwargs)
        except Exception:
            return None
        else:
            return obj