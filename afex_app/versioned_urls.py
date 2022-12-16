from django.urls import path, include
from django.http.response import HttpResponse
from django.contrib import admin


def home_view(request):
    """Server health check"""

    return HttpResponse("All is well")


urlpatterns = [
    path("v1/", include("afex_app.urls")),
    path('admin/', admin.site.urls),
    path('', home_view, name="health_check"),
]