"""Mixins for i18n_fields functionality."""

from typing import Any

from django.db import transaction
from django.db.utils import IntegrityError

from .settings import i18n_fields_settings


class AtomicSlugRetryMixin:
    """Mixin that enables LocalizedUniqueSlugField retry on UNIQUE constraint violation.

    Models using LocalizedUniqueSlugField must inherit from this mixin
    to enable automatic retry with incremented slug suffix on conflicts.

    Example:
        class Article(AtomicSlugRetryMixin, models.Model):
            title = LocalizedCharField()
            slug = LocalizedUniqueSlugField(populate_from='title')
    """

    retries: int = 0

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save the model with atomic slug retry on UNIQUE constraint violation.

        Args:
            *args: Positional arguments passed to parent save().
            **kwargs: Keyword arguments passed to parent save().
        """
        max_retries = i18n_fields_settings.MAX_RETRIES

        if not hasattr(self, "retries"):
            self.retries = 0

        with transaction.atomic():
            try:
                super().save(*args, **kwargs)  # type: ignore[misc]
                return
            except IntegrityError as ex:
                if "slug" not in str(ex):
                    raise ex

                if self.retries >= max_retries:
                    raise ex

        self.retries += 1
        self.save(*args, **kwargs)
