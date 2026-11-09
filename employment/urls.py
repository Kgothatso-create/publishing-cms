from django.urls import include, path
from .views import *


urlpatterns = [
    path("", employee_dashboard, name="employee_dashboard"),
    path("my-profile/", employee_profile, name="employee_profile"),
    path("employees/",
         include([
             path("", employee_list, name="employee_list"),
             path("add/", employee_create, name="employee-create"),
             path("<uuid:id>/", include([
                 path("", employee_detail, name="employee_detail"),
                 path("edit/", employee_edit, name="employee_edit"),
                 path("delete/", employee_delete, name="employee_delete"), ])),
         ])),
    path("roles/",
         include([
             path("", role_list, name="role_list", ),
             path("add/", role_create, name="role_create", ),
             path("<uuid:id>/", include([
                 path("", role_detail, name="role_detail"),
                 path("edit/", role_edit, name="role_edit"),
                 path("delete/", role_delete, name="role_delete"),
             ])),
         ])),
    path("calendar/", include([
        path("", calendar_view, name="calendar"),
        path("create-event/", create_company_event, name="create_company_event"),
        path("company-events/", company_events, name="company_events"),
        path(
            "company-events/<uuid:event_id>/", include([
                path("", company_event_detail, name="company_event_detail"),
                path("edit/", edit_company_event, name="edit_company_event", ),
                path("delete/", delete_company_event, name="delete_company_event", ),
            ])),
    ])),
    path("users/", user_list, name="user_list"),
    path("users/<str:id>/", user_detail, name="user_detail"),
    path("notifications/", include([
        path("create/",
             create_notification,
             name="create_notification"
             ),
    ]), )
]
