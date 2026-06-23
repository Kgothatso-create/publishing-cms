from django.contrib import admin
from .models import PersonProfile, PersonIdentityDocument


@admin.register(PersonProfile)
class PersonProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", "get_email", "gender", "race", "city",
        "province", "country", "updated_at",
    )

    search_fields = (
        "user__username", "user__email", "user__first_name", "user__last_name",
    )

    list_filter = (
        "gender", "race", "country", "province",
    )

    readonly_fields = ("created_at", "updated_at",)

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"


@admin.register(PersonIdentityDocument)
class PersonIdentityDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "user", "document_type", "identification_document_number", "issued_country",
        "issue_date", "expiry_date", "is_primary", "created_at",
    )

    search_fields = (
        "user__username", "user__email", "identification_document_number",
    )

    list_filter = (
        "document_type", "issued_country", "is_primary",
    )

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)
