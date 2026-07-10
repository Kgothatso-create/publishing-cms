from django.urls import path
from .views import *

urlpatterns = [
    path("subscribe-newsletter/", subscribe_newsletter, name="subscribe newsletter"),
    path("register/", register_view, name="register view"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
]
