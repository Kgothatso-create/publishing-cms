from django.contrib import admin
from .models import Employment, Role


# -----------------------------
# ROLE ADMIN
# -----------------------------

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "created_at")
    search_fields = ("name", "code")
    list_filter = ("is_active",)
    ordering = ("name",)

    fieldsets = (
        ("Role Information", {
            "fields": ("name", "code", "description", "is_active")
        }),
    )


# -----------------------------
# EMPLOYMENT ADMIN
# -----------------------------

@admin.register(Employment)
class EmploymentAdmin(admin.ModelAdmin):
    list_display = (
        "employee_number",
        "user",
        "job",
        "role",
        "status",
        "employment_type",
        "hire_date",
    )

    list_filter = (
        "status",
        "employment_type",
        "role",
        "job",
        "location",
    )

    search_fields = (
        "employee_number",
        "user__email",
        "user__username",
        "job__title",
        "role__name",
    )

    ordering = ("-created_at",)

    raw_id_fields = ("user", "job", "role", "manager")

    date_hierarchy = "hire_date"

    fieldsets = (
        ("Employee Identity", {
            "fields": ("employee_number", "user")
        }),

        ("Job Assignment", {
            "fields": ("job", "role", "manager")
        }),

        ("Employment Status", {
            "fields": ("status", "employment_type")
        }),

        ("Lifecycle Dates", {
            "fields": ("hire_date", "probation_end_date", "termination_date")
        }),

        ("Organization Context", {
            "fields": ("location", "cost_center")
        }),
    )
