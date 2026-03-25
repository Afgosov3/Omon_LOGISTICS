from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import DispatcherLoginView, MeView

urlpatterns = [
    path("login/", DispatcherLoginView.as_view(), name="dispatcher-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
]

