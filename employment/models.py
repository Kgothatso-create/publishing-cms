import uuid

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


# -----------------------------
# ROLE MODEL
# -----------------------------

class Role(models.Model):
    """
    Employment-level role (NOT Django permissions group).
    Example: Team Lead, Supervisor, Assistant.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "employment_role"
        ordering = ["name"]

    def __str__(self):
        return self.name


# -----------------------------
# EMPLOYMENT MODEL
# -----------------------------

class Employment(models.Model):
    """
    Represents a user's job assignment within the organization.
    """

    class EmploymentStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        TERMINATED = "TERMINATED", "Terminated"
        ON_LEAVE = "ON_LEAVE", "On Leave"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_number = models.CharField(max_length=50, unique=True, db_index=True)
    employee_email = models.EmailField(unique=True, db_index=True, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employment",
    )
    job = models.ForeignKey(
        "job.Job", on_delete=models.PROTECT, related_name="employments", null=True, blank=True
    )
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name="employments",
    )
    manager = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="team_members",
    )
    status = models.CharField(
        max_length=20, choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE, db_index=True,
    )
    employment_type = models.CharField(
        max_length=20, choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    hire_date = models.DateField()
    probation_end_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    cost_center = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "employment_employment"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status="ACTIVE"),
                name="unique_active_employment_per_user",
            )
        ]

    # -------------------------
    # VALIDATION LOGIC
    # -------------------------
    def clean(self):
        """
        Business rules enforcement at model level.
        """

        # Rule 1: Terminated must have termination date
        if self.status == self.EmploymentStatus.TERMINATED and not self.termination_date:
            raise ValidationError(
                {"termination_date": "Termination date is required for terminated employment."}
            )

        # Rule 2: Active employment must have hire date
        if self.status == self.EmploymentStatus.ACTIVE and not self.hire_date:
            raise ValidationError(
                {"hire_date": "Hire date is required for active employment."}
            )

        # Rule 3: Prevent termination date before hire date
        if self.termination_date and self.hire_date:
            if self.termination_date < self.hire_date:
                raise ValidationError(
                    {"termination_date": "Termination date cannot be before hire date."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_number} - {self.user}"


# -----------------------------
# EMPLOYEE PROFILE MODEL
# -----------------------------

class EmployeeProfile(models.Model):
    """
    Stores personal information for employees.
    Every employee has one profile.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employment = models.OneToOneField(
        Employment,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Personal Information
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)

    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="South Africa")

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    # System Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "employment_employee_profile"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Notification(models.Model):
    """
    Stores notifications for employees.
    Example: Article reports, user issues, system alerts.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employment,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    link = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional URL to the related item."
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employment_notification"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class CompanyEvent(models.Model):
    """
    Stores company-wide events.
    Example: Birthdays, meetings, holidays, announcements.
    """

    class EventType(models.TextChoices):
        BIRTHDAY = "BIRTHDAY", "Birthday"
        MEETING = "MEETING", "Meeting"
        HOLIDAY = "HOLIDAY", "Holiday"
        TRAINING = "TRAINING", "Training"
        ANNOUNCEMENT = "ANNOUNCEMENT", "Announcement"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150)
    description = models.TextField(
        blank=True,
        null=True,
    )
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.ANNOUNCEMENT,
    )
    event_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_company_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employment_company_event"
        ordering = ["event_date"]

    def __str__(self):
        return self.title