from django.urls import include, path
from .views import *

urlpatterns = [
    path("", employee_dashboard, name="employee-dashboard"),
    path("employees/",
         include([
             path("", employee_list, name="employee-list"),
             path("add/", employee_create, name="employee-create"),
         ])),
    path("roles/",
         include([
             path("roles/", role_list, name="role-list", ),
             path("roles/add/", role_create, name="role-create", ),
         ])),
]
