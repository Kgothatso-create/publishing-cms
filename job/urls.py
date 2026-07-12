from django.urls import include, path
from .views import *

urlpatterns = [
    path("job/",
         include([
             path("", job_list, name="job-list"),
             path("add/", job_create, name="job-create")
         ])),
    path("department/", include([
        path("", department_list, name="department-list"),
        path("add/", department_create, name="department-create")
    ])),
]
