from django.contrib import admin
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    list_display = (
        "title", "category", "author", "status", "is_featured",
        "created_at", "published_at",
    )

    list_filter = (
        "status", "category", "is_featured", "created_at",
    )

    search_fields = (
        "title", "subheading", "excerpt", "body",
    )

    prepopulated_fields = {"slug": ("title",)}

    date_hierarchy = "created_at"

    ordering = ("-created_at",)
