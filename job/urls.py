from django.urls import path
from .views import *

urlpatterns = [
    path(
        "",
        job_list,
        name="job-list"
    ),
    path(
        "add/",
        job_create,
        name="job-create"
    ),
]