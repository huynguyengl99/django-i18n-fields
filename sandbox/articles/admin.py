"""Admin configuration for articles app."""

from django.contrib import admin

from i18n_fields import LocalizedFieldsAdminMixin

from .models import Article, Category, Tag


@admin.register(Category)
class CategoryAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    """Admin for Category model with localized fields."""

    list_display = ["name", "id"]
    search_fields = ["name"]



@admin.register(Article)
class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    """Admin for Article model with localized fields.

    Demonstrates tab display mode (default).
    """
    localized_fields_display = "dropdown"


    list_display = ["title", "category", "published", "created_at"]
    list_filter = ["published", "category", "created_at"]
    search_fields = ["title", "content"]
    readonly_fields = ["slug", "created_at", "updated_at"]
    raw_id_fields = ["category"]

    fieldsets = [
        (None, {"fields": ["title", "slug", "summary", "content"]}),
        ("Metadata", {"fields": ["view_count", "rating", "is_featured"]}),
        ("Relations", {"fields": ["category"]}),
        ("Status", {"fields": ["published", "created_at", "updated_at"]}),
    ]


@admin.register(Tag)
class TagAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    """Admin for Tag model with dropdown display mode."""

    # Override display mode for this specific admin
    localized_fields_display = "dropdown"

    list_display = ["name", "id"]
    search_fields = ["name"]
    filter_horizontal = ["articles"]
