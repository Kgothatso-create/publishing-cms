from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class OnboardingStatus(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"


class User(AbstractUser):
    onboarding_status = models.CharField(
        max_length=20,
        choices=OnboardingStatus.choices,
        default=OnboardingStatus.NOT_STARTED
    )


class PersonProfile(models.Model):
    """
    Stores personal information about a user.
    This is separate from authentication and employment data.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    gender = models.CharField(max_length=20, blank=True)
    race = models.CharField(max_length=50, blank=True)

    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class PersonIdentityDocument(models.Model):
    """
    Stores multiple identity documents per user.
    Supports ID, passport, work permits, etc.
    """

    class DocumentType(models.TextChoices):
        ID_CARD = "id_card", "ID Card"
        PASSPORT = "passport", "Passport"
        WORK_PERMIT = "work_permit", "Work Permit"
        DRIVERS_LICENSE = "drivers_license", "Driver's License"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="identity_documents"
    )
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    file = models.FileField(upload_to="identity_documents/")
    issued_country = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    identification_document_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_document_type_display()}"
