from django.contrib import admin
from .models import EmployeeProfile, Employment, Role


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


@admin.register(Employment)
class EmploymentAdmin(admin.ModelAdmin):
    list_display = (
        "employee_number",
        "employee_email",
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
            "fields": ("employee_number", "user", "employee_email")
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


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "employment",
        "phone_number",
        "city",
        "province",
        "country",
    )

    list_filter = (
        "province",
        "city",
        "country",
    )

    search_fields = (
        "first_name",
        "last_name",
        "phone_number",
        "employment__employee_number",
        "employment__user__email",
    )

    ordering = ("last_name", "first_name")

    raw_id_fields = ("employment",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Employee", {
            "fields": ("employment",)
        }),

        ("Personal Information", {
            "fields": (
                "first_name",
                "last_name",
                "date_of_birth",
            )
        }),

        ("Contact Information", {
            "fields": (
                "phone_number",
                "address_line_1",
                "address_line_2",
                "city",
                "province",
                "postal_code",
                "country",
            )
        }),

        ("Emergency Contact", {
            "fields": (
                "emergency_contact_name",
                "emergency_contact_phone",
            )
        }),

        ("System Information", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
