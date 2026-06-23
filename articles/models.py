from datetime import timezone

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
    STATUS_RETRACTED = "retracted"

    STATUS_CHOICES = (
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_RETRACTED, "Retracted"),
    )

    category = models.ForeignKey("Category", on_delete=models.PROTECT, related_name="articles")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    subheading = models.CharField(max_length=255, blank=True)
    excerpt = models.TextField()
    body = models.TextField()
    featured_image = models.ImageField(upload_to="articles/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
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
        self.save(update_fields=["status", "published_at", "updated_at"])

    def unpublish(self):
        self.status = self.STATUS_DRAFT
        self.save(update_fields=["status", "updated_at"])

    def __str__(self):
        return self.title
