from django.urls import path
from .views import login_view, register_view, subscribe_newsletter

urlpatterns = [
    path("subscribe-newsletter/", subscribe_newsletter, name="subscribe newsletter"),
    path("register/", register_view, name="register view"),
    path("login/", login_view, name="login"),
]
