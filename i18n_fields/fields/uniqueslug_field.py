"""LocalizedUniqueSlugField for automatic unique slug generation."""

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any

from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import translation
from django.utils.text import slugify

from ..mixins import AtomicSlugRetryMixin
from ..util import get_language_codes, resolve_object_property
from ..value import LocalizedValue
from .field import LocalizedField

if TYPE_CHECKING:
    from django.db import models

# Maximum number of attempts to generate a unique slug before falling back to timestamp
MAX_UNIQUE_SLUG_ATTEMPTS = 1000


class LocalizedUniqueSlugField(LocalizedField):
    """Automatically generates unique slugs for a localized field.

    This field generates slugs from another field's values and ensures
    uniqueness by appending a counter or timestamp on collision.

    Models using this field MUST inherit from AtomicSlugRetryMixin.

    Example:
        class Article(AtomicSlugRetryMixin, models.Model):
            title = LocalizedCharField()
            slug = LocalizedUniqueSlugField(populate_from='title')
    """

    def __init__(
        self,
        *args: Any,
        populate_from: str | tuple[str, ...] | Callable[..., str],
        include_time: bool = False,
        uniqueness: list[str] | None = None,
        enabled: bool = True,
        immutable: bool = False,
        **kwargs: Any,
    ):
        """Initialize the unique slug field.

        Args:
            populate_from: Field name(s) or callable to generate slug from.
            include_time: Whether to include microseconds in slug.
            uniqueness: List of language codes to enforce uniqueness for.
            enabled: Whether slug generation is enabled.
            immutable: Whether to prevent slug changes after creation.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        self.populate_from = populate_from
        self.include_time = include_time
        self.uniqueness = uniqueness or get_language_codes()
        self.enabled = enabled
        self.immutable = immutable

        super().__init__(*args, **kwargs)

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        """Deconstruct the field for migrations.

        Returns:
            Tuple of (name, path, args, kwargs).
        """
        name, path, args, kwargs = super().deconstruct()

        kwargs["populate_from"] = self.populate_from
        kwargs["include_time"] = self.include_time

        if self.uniqueness != get_language_codes():
            kwargs["uniqueness"] = self.uniqueness

        if not self.enabled:
            kwargs["enabled"] = self.enabled

        if self.immutable:
            kwargs["immutable"] = self.immutable

        return name, path, args, kwargs

    def formfield(self, **kwargs: Any) -> forms.Field:  # type: ignore[override]
        """Get the form field (hidden since slug is auto-generated).

        Args:
            **kwargs: Keyword arguments for the form field.

        Returns:
            Hidden form field.
        """
        defaults = {"form_class": forms.CharField, "required": False}
        defaults.update(kwargs)

        form_field = super().formfield(**defaults)
        form_field.widget = forms.HiddenInput()

        return form_field  # type: ignore[no-any-return]

    def pre_save(self, model_instance: "models.Model", add: bool) -> LocalizedValue:
        """Generate the slug before saving.

        Args:
            model_instance: The model instance being saved.
            add: Whether this is a new instance.

        Returns:
            The generated LocalizedValue with slugs.

        Raises:
            ImproperlyConfigured: If model doesn't use AtomicSlugRetryMixin.
        """
        if not self.enabled:
            return getattr(model_instance, self.name)  # type: ignore[no-any-return]

        if not isinstance(model_instance, AtomicSlugRetryMixin):
            raise ImproperlyConfigured(
                f"Model '{type(model_instance).__name__}' does not inherit from "
                "AtomicSlugRetryMixin. Without this, LocalizedUniqueSlugField "
                "will not work properly."
            )

        slugs = LocalizedValue()
        retries = getattr(model_instance, "retries", 0)

        for lang_code, value in self._get_populate_values(model_instance):
            if not value:
                continue

            slug = slugify(value, allow_unicode=True)

            current_slug = getattr(model_instance, self.name).get(lang_code)
            if current_slug and self.immutable:
                slugs.set(lang_code, current_slug)
                continue

            # Check if slug needs regeneration
            if model_instance.pk is not None and current_slug is not None:
                current_slug_end_index = current_slug.rfind("-")
                if current_slug_end_index > 0:
                    stripped_slug = current_slug[:current_slug_end_index]
                    if slug == stripped_slug:
                        slugs.set(lang_code, current_slug)
                        continue

            if self.include_time:
                slug += f"-{datetime.now().microsecond}"

            if retries > 0:
                if not self.include_time:
                    slug += "-"
                slug += str(retries)

            # Check uniqueness in database if this language is in uniqueness list
            if lang_code in self.uniqueness:
                slug = self._make_unique_slug(model_instance, lang_code, slug, retries)

            slugs.set(lang_code, slug)

        setattr(model_instance, self.name, slugs)
        return slugs

    def _make_unique_slug(
        self,
        model_instance: "models.Model",
        lang_code: str,
        slug: str,
        retries: int,
    ) -> str:
        """Ensure the slug is unique by checking the database.

        Args:
            model_instance: The model instance.
            lang_code: The language code.
            slug: The base slug.
            retries: Current retry count.

        Returns:
            A unique slug.
        """
        from django.db.models.fields.json import KeyTextTransform

        model = model_instance.__class__
        qs = model._default_manager.annotate(
            _slug_value=KeyTextTransform(lang_code, self.name)
        ).filter(_slug_value=slug)

        # Exclude current instance if it exists
        if model_instance.pk is not None:
            qs = qs.exclude(pk=model_instance.pk)

        if not qs.exists():
            return slug

        # Slug exists, need to make it unique
        # If we have retries, the retry suffix is already added
        if retries > 0:
            return slug

        # Find the next available suffix
        counter = 1
        base_slug = slug
        while True:
            new_slug = f"{base_slug}-{counter}"
            qs = model._default_manager.annotate(
                _slug_value=KeyTextTransform(lang_code, self.name)
            ).filter(_slug_value=new_slug)

            if model_instance.pk is not None:
                qs = qs.exclude(pk=model_instance.pk)

            if not qs.exists():
                return new_slug

            counter += 1
            if counter > MAX_UNIQUE_SLUG_ATTEMPTS:
                # Fall back to timestamp
                return f"{base_slug}-{datetime.now().microsecond}"

    def _get_populate_values(
        self, model_instance: "models.Model"
    ) -> list[tuple[str, str]]:
        """Get values to populate slugs from.

        Args:
            model_instance: The model instance.

        Returns:
            List of (lang_code, value) tuples.
        """
        return [
            (
                lang_code,
                self._get_populate_from_value(
                    model_instance, self.populate_from, lang_code
                ),
            )
            for lang_code, _ in settings.LANGUAGES
        ]

    @staticmethod
    def _get_populate_from_value(
        model_instance: Any,
        field_name: str | tuple[str, ...] | Callable[..., str],
        language: str,
    ) -> str:
        """Get the value to create a slug from.

        Args:
            model_instance: The model instance.
            field_name: Field name(s) or callable.
            language: The language code.

        Returns:
            The text to generate a slug from.
        """
        if callable(field_name):
            return field_name(model_instance)

        def get_field_value(name: str) -> str:
            value = resolve_object_property(model_instance, name)
            with translation.override(language):
                return str(value)

        if isinstance(field_name, tuple | list):
            values = [get_field_value(name) for name in field_name]
            return "-".join(v for v in values if v)

        return get_field_value(field_name)
