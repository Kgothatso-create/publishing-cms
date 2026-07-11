from django.urls import path
from .views import *

urlpatterns = [
    path("", employee_dashboard, name="employee-dashboard"),
]
