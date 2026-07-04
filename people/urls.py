from django.urls import path
from .views import subscribe_newsletter

urlpatterns = [
    path("subscribe-newsletter/", subscribe_newsletter, name="subscribe newsletter"),
]
