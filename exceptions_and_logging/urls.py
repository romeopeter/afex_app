from django.urls import path

from .views import DRFView



urlpatterns = [
    path("drf/<slug:error_type>/", DRFView.as_view())
]