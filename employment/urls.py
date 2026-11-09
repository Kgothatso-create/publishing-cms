from django.urls import include, path
from .views import *

urlpatterns = [
    path("", employee_dashboard, name="employee_dashboard"),
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
    path("calendar/", include([
        path("", calendar_view, name="calendar"),
        path("create-event/", create_company_event, name="create_company_event"),
        path("company-events/", company_events, name="company_events"),
        path(
            "company-events/<uuid:event_id>/", include([
                path("", company_event_detail, name="company_event_detail"),
                path("edit/", edit_company_event, name="edit_company_event",),
                path("delete/", delete_company_event, name="delete_company_event",),
            ])),
    ])),
]
