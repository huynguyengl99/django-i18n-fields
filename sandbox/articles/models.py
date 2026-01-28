"""Article models for testing i18n_fields."""

from django.db import models

from i18n_fields import (
    AtomicSlugRetryMixin,
    LocalizedBooleanField,
    LocalizedCharField,
    LocalizedFloatField,
    LocalizedIntegerField,
    LocalizedTextField,
    LocalizedUniqueSlugField,
)


class Category(models.Model):
    """Category model with localized name."""

    name = LocalizedCharField(required=["en"], max_length=100)
    description = LocalizedTextField(blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return str(self.name)


class Article(AtomicSlugRetryMixin, models.Model):
    """Article model demonstrating all localized field types."""

    # Basic localized text fields
    title = LocalizedCharField(required=["en"], max_length=200)
    slug = LocalizedUniqueSlugField(populate_from="title", include_time=False)
    summary = LocalizedCharField(blank=True, max_length=500)
    content = LocalizedTextField(blank=True)

    # Localized typed fields
    view_count = LocalizedIntegerField(blank=True)
    rating = LocalizedFloatField(blank=True)
    is_featured = LocalizedBooleanField(blank=True)

    # Regular Django fields
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.title)


class Tag(models.Model):
    """Simple tag model with localized name."""

    name = LocalizedCharField(required=["en"], max_length=50)
    articles = models.ManyToManyField(Article, related_name="tags", blank=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self) -> str:
        return str(self.name)
