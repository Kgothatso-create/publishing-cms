from django.urls import include, path
from .views import *

urlpatterns = [
    path("job/",
         include([
             path("", job_list, name="job_list"),
             path("<uuid:id>/", include([
                 path("", job_detail, name="job_detail"),
                 path("edit/", job_edit, name="job_edit"),
                 path("delete/", job_delete, name="job_delete",)
             ])),
             path("add/", job_create, name="job-create")
         ])),
    path("department/", include([
        path("", department_list, name="department_list"),
        path("add/", department_create, name="department-create"),
        path("<uuid:id>/", include([
            path("", department_detail, name="department_detail"),
            path("edit/", department_edit, name="department_edit"),
            path("delete/", department_delete, name="department_delete",),
        ])),
    ])),
]
