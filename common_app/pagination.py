"""App-wide pagination settings"""


from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from  drf_spectacular.utils import OpenApiParameter, OpenApiTypes


class GeneralPagingation(PageNumberPagination):
    max_page_size = 20
    page_size = 10
    page_query_param = "page"
    page_size_query_description = "page_size"

    def get_paginated_response(self, data):
        response = Response(data)
        response['count'] = self.page.paginator.count
        response['next'] = self.get_next_link()
        response['previous'] = self.get_previous_link()
        return response
    
    def get_paginated_response_schema(self, schema):
        return schema


# Open API parameters for pagination, in response headers.
count = OpenApiParameter(
    "count", type=OpenApiTypes.INT, location=OpenApiParameter.HEADER,
    required=False, response=[200],
    description="Total number of objects to display."
)

next = OpenApiParameter(
    "next", type=OpenApiTypes.URI, location=OpenApiParameter.HEADER,
    required=False, response=[200],
    description="Url to next set of objects to display."
)

previous = OpenApiParameter(
    "previous", type=OpenApiTypes.URI, location=OpenApiParameter.HEADER,
    required=False, response=[200],
    description="Url to previous set of objects to display."
)

paginator_header_params = [count, next, previous]