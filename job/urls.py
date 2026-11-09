from django.urls import include, path
from .views import *

urlpatterns = [
    path("job/",
         include([
             path("", job_list, name="job-list"),
             path(
                 "<uuid:id>/",
                 job_detail,
                 name="job_detail"
             ),
             path("add/", job_create, name="job-create")
         ])),
    path("department/", include([
        path("", department_list, name="department-list"),
        path("add/", department_create, name="department-create"),
        path("<uuid:id>/", department_detail, name="department_detail"),
    ])),
]
