from .models import NewsletterSubscriber


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # -------------------------
    # LIST VIEW
    # -------------------------
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "onboarding_status",
    )

    # -------------------------
    # EDIT USER (existing user)
    # -------------------------
    fieldsets = UserAdmin.fieldsets + (
        ("Onboarding", {
            "fields": ("onboarding_status",)
        }),
    )

    # -------------------------
    # CREATE USER (IMPORTANT)
    # -------------------------
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "first_name",
                "last_name",
                "password1",
                "password2",
                "onboarding_status",
            ),
        }),
    )

    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "is_active",
        "subscribed_at",
    )
    list_filter = (
        "is_active",
        "subscribed_at",
    )
    search_fields = (
        "email",
    )
    ordering = (
        "-subscribed_at",
    )
