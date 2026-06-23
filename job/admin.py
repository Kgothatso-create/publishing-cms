from django.contrib import admin
from .models import Department, Job


# -----------------------------
# DEPARTMENT ADMIN
# -----------------------------

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
    )

    list_filter = (
        "is_active",
    )

    ordering = ("name",)

    fieldsets = (
        ("Department Details", {
            "fields": ("name", "code", "description", "is_active")
        }),
    )


# -----------------------------
# JOB ADMIN
# -----------------------------

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "job_code",
        "title",
        "department",
        "is_active",
        "created_at",
    )

    list_filter = (
        "department",
        "is_active",
    )

    search_fields = (
        "job_code",
        "title",
        "department__name",
    )

    ordering = ("title",)

    raw_id_fields = ("department",)

    fieldsets = (
        ("Job Identity", {
            "fields": ("job_code", "title", "description")
        }),

        ("Organization Structure", {
            "fields": ("department",)
        }),

        ("Job Configuration", {
            "fields": ("is_active", "level", "grade")
        }),
    )
