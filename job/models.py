import uuid

from django.db import models


# -----------------------------
# DEPARTMENT MODEL
# -----------------------------

class Department(models.Model):
    """
    Represents an organizational department.
    Example: Engineering, HR, Finance.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)

    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "jobs_department"
        ordering = ["name"]

    def __str__(self):
        return self.name


# -----------------------------
# JOB MODEL
# -----------------------------

class Job(models.Model):
    """
    Represents a job definition within the organization.
    This is NOT an employee record — it is a reusable position template.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # -------------------------
    # Identity
    # -------------------------
    job_code = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=150)

    description = models.TextField(blank=True, null=True)

    # -------------------------
    # Organization Structure
    # -------------------------
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="jobs",
    )

    # -------------------------
    # Job Properties
    # -------------------------
    is_active = models.BooleanField(default=True)

    # Optional future expansion (useful for HR systems)
    level = models.CharField(max_length=50, blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, null=True)

    # -------------------------
    # System Fields
    # -------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -------------------------
    # META
    # -------------------------
    class Meta:
        db_table = "jobs_job"
        ordering = ["title"]

        constraints = [
            models.UniqueConstraint(
                fields=["title", "department"],
                name="unique_job_title_per_department",
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.job_code})"