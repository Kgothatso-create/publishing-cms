from django.utils import timezone

from django.db import models
from django.conf import settings


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Category(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Article(BaseModel):

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_REJECTED = "rejected"
    STATUS_APPROVED = "approved"
    STATUS_RETRACTED = "retracted"

    STATUS_CHOICES = (
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_RETRACTED, "Retracted"),
    )

    REVIEW_NOT_REVIEWED = "not_reviewed"
    REVIEW_UNDER_REVIEW = "under_review"
    REVIEW_APPROVED = "approved"
    REVIEW_NEEDS_CHANGES = "needs_changes"

    REVIEW_STATUS_CHOICES = (
        (REVIEW_NOT_REVIEWED, "Not Reviewed"),
        (REVIEW_UNDER_REVIEW, "Under Review"),
        (REVIEW_APPROVED, "Approved"),
        (REVIEW_NEEDS_CHANGES, "Needs Changes"),
    )

    category = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="articles"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles"
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    body = models.TextField()

    featured_image = models.ImageField(
        upload_to="articles/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )

    review_status = models.CharField(
        max_length=30,
        choices=REVIEW_STATUS_CHOICES,
        default=REVIEW_NOT_REVIEWED
    )

    last_reviewed_at = models.DateTimeField(
        blank=True, null=True
    )

    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def publish(self):
        """
        Core CMS behavior:
        Moves article into published state safely.
        """
        self.status = self.STATUS_PUBLISHED
        if not self.published_at:
            self.published_at = timezone.now()

        self.review_status = self.REVIEW_NOT_REVIEWED

        self.save(
            update_fields=["status", "published_at", "review_status", "updated_at"]
        )

    def unpublish(self):
        """
        Core CMS behavior:
        Moves article into draft state safely.
        """
        self.status = self.STATUS_DRAFT
        self.save(update_fields=["status", "updated_at"])

    def retract(self):
        """
        Core CMS behavior:
        Moves a published article into a retracted state.
        """
        self.status = self.STATUS_RETRACTED
        self.save(update_fields=["status", "updated_at"])

    def approve(self):
        """
        Core CMS behavior:
        Moves an article into an approved state.
        """
        self.status = self.STATUS_REJECTED

        self.save(
            update_fields=["status", "updated_at"]
        )

    def reject(self):
        """
        Core CMS behavior:
        Moves an article into a rejected state.
        """
        self.status = self.STATUS_REJECTED

        self.save(
            update_fields=["status", "updated_at"]
        )

    def mark_reviewed(self, status):
        """
        Updates article review state.
        """
        self.review_status = status
        self.last_reviewed_at = timezone.now()

        self.save(
            update_fields=["review_status", "last_reviewed_at", "updated_at"]
        )

    def has_reports(self):
        return self.reports.filter(resolved=False).exists()

    def __str__(self):
        return self.title


class ArticleReport(BaseModel):

    REASON_OFFENSIVE = "offensive"
    REASON_DISTURBING = "disturbing"
    REASON_MISLEADING = "misleading"
    REASON_SPAM = "spam"
    REASON_GUIDELINE = "guideline"

    REASON_CHOICES = (
        (REASON_OFFENSIVE, "Offensive Content"),
        (REASON_DISTURBING, "Disturbing Content"),
        (REASON_MISLEADING, "Misleading Information"),
        (REASON_SPAM, "Spam"),
        (REASON_GUIDELINE, "Violates Guidelines"),
    )

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="reports"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_reports"
    )

    reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    resolved = models.BooleanField(
        default=False
    )

    resolved_at = models.DateTimeField(
        blank=True,
        null=True
    )

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="resolved_article_reports"
    )

    class Meta:
        ordering = ["-created_at"]

    @property
    def report_count(self):
        return self.reports.filter(
            resolved=False
        ).count()
