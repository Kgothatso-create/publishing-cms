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

    # -------------------------
    # Identity & Relationships
    # -------------------------
    employee_number = models.CharField(max_length=50, unique=True, db_index=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employment",
    )

    job = models.ForeignKey(
        "job.Job",
        on_delete=models.PROTECT,
        related_name="employments",
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="employments",
    )

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members",
    )

    # -------------------------
    # Employment Status
    # -------------------------
    status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
        db_index=True,
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )

    # -------------------------
    # Lifecycle Dates
    # -------------------------
    hire_date = models.DateField()
    probation_end_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)

    # -------------------------
    # Organizational Context
    # -------------------------
    location = models.CharField(max_length=150, null=True, blank=True)
    cost_center = models.CharField(max_length=100, null=True, blank=True)

    # -------------------------
    # System Fields
    # -------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -------------------------
    # META
    # -------------------------
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
