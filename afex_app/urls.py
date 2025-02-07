"""afex_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

# drfm
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

# application views
# from registration.views import (UserViewsets)

from registration.views.user import UserViewsets
from registration.views.registration import RegistrationViewsets
from chats.views import ChatViewset


router = DefaultRouter()

router.register(r"registration", RegistrationViewsets, "registration")
router.register(r"users", UserViewsets, "users")
router.register(r'chats', ChatViewset, "chats")

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema_view"),
    path("swagger_ui/", SpectacularSwaggerView.as_view(url_name="schema_view"), name="swagger_view"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls
