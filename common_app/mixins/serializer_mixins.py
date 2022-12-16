"""Common functionalities for serializer"""


class BaseSerializerMixin:

    """Helper functions for serializer"""

    def __init__(self, instance=None, **kwargs):
        skip_fields = kwargs.pop("skip", [])
        super().__init__(instance, **kwargs)
        
        if skip_fields:
            self.skip = skip_fields
            self.fields = {
                k: v 
                for k, v in self.fields.items() if k not in skip_fields
            }


class DisplaySerializerMixin(BaseSerializerMixin):
    """Utility methods for display serializers."""

    err_msg = "This class accepts no data. Strictly for display purposes."

    def __init__(self, instance=None, **kwargs):
        assert kwargs.get("data") is None, self.err_msg
        super().__init__(instance, **kwargs)


class URLParamsSerializerMixin:
    """Methods needed for url params processing.
    
    - Basically all serializers that use this mixin will have all their
      fields as ListSerializers.

    - Single value fields should be validated automatically to extract its value
      from the list, fields with multiple values can declare validate_<field_name>
      methods to return a list.

    - The label for each field will mirror the db query parameter which the
      value for that field will be paired with to query the database.
    """

    def __init__(self, instance=None, **kwargs) -> None:
        super().__init__(instance, **kwargs)
        # Most fields will return their first list value on validation.
        # No need hardcoding this, automate this if user didn't provide
        # an explicit validate_<field_name> method.
        for k, _ in self.fields.items():
            if not hasattr(self, f"validate_{k}"):
                setattr(self, f"validate_{k}", self.return_validated_field)

    @staticmethod
    def return_validated_field(value):
        return value[0]

    def db_query_params(self) -> dict:
        """Returns db query params for loans"""

        final_query = {}
        for k, v in self.validated_data.items():
            if isinstance(v, list):
                # Queries that sport multiple values e.g
                # User.objects.filter(friends__first_name="Jon", friends__last_name="Doe")
                # can be done by adding the label "friends__first_name,friends__last_name" to
                # the friends field. This field's validated value must be same length
                # with the label (if split at ','), in this case, 2.
                # This branch of the subroutine caters for cases like this.
                sub_query_fields = self.fields[k].label.split(",")
                assert len(sub_query_fields) == len(v), "Split labels and validated value should be of same length"
                idx = 0
                for value in v:
                    final_query.update({sub_query_fields[idx]: value})
                    idx += 1
            else:
                final_query.update({self.fields[k].label: v})
        return final_query