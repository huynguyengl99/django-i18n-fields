"""Tests for LocalizedUniqueSlugField."""

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db.utils import IntegrityError

import pytest
from i18n_fields.fields import LocalizedCharField, LocalizedUniqueSlugField
from i18n_fields.mixins import AtomicSlugRetryMixin

from .fake_model import cleanup_fake_model, get_fake_model


class TestLocalizedUniqueSlugFieldInit:
    """Tests for LocalizedUniqueSlugField initialization."""

    def test_populate_from_string(self) -> None:
        """Test populate_from with string field name."""
        field = LocalizedUniqueSlugField(populate_from="title")
        assert field.populate_from == "title"

    def test_populate_from_tuple(self) -> None:
        """Test populate_from with tuple of field names."""
        field = LocalizedUniqueSlugField(populate_from=("title", "subtitle"))
        assert field.populate_from == ("title", "subtitle")

    def test_populate_from_callable(self) -> None:
        """Test populate_from with callable."""

        def get_slug(instance):
            return instance.title

        field = LocalizedUniqueSlugField(populate_from=get_slug)
        assert field.populate_from == get_slug

    def test_include_time_default(self) -> None:
        """Test include_time defaults to False."""
        field = LocalizedUniqueSlugField(populate_from="title")
        assert field.include_time is False

    def test_include_time_true(self) -> None:
        """Test include_time can be set to True."""
        field = LocalizedUniqueSlugField(populate_from="title", include_time=True)
        assert field.include_time is True

    def test_uniqueness_default(self) -> None:
        """Test uniqueness defaults to all languages."""
        field = LocalizedUniqueSlugField(populate_from="title")
        # Should contain all language codes
        from i18n_fields.util import get_language_codes

        assert field.uniqueness == get_language_codes()

    def test_uniqueness_custom(self) -> None:
        """Test uniqueness can be set to specific languages."""
        field = LocalizedUniqueSlugField(populate_from="title", uniqueness=["en"])
        assert field.uniqueness == ["en"]

    def test_enabled_default(self) -> None:
        """Test enabled defaults to True."""
        field = LocalizedUniqueSlugField(populate_from="title")
        assert field.enabled is True

    def test_immutable_default(self) -> None:
        """Test immutable defaults to False."""
        field = LocalizedUniqueSlugField(populate_from="title")
        assert field.immutable is False


class TestLocalizedUniqueSlugFieldDeconstruct:
    """Tests for LocalizedUniqueSlugField.deconstruct."""

    def test_deconstruct_includes_populate_from(self) -> None:
        """Test deconstruct includes populate_from."""
        field = LocalizedUniqueSlugField(populate_from="title")
        name, path, args, kwargs = field.deconstruct()

        assert "populate_from" in kwargs
        assert kwargs["populate_from"] == "title"

    def test_deconstruct_includes_include_time(self) -> None:
        """Test deconstruct includes include_time."""
        field = LocalizedUniqueSlugField(populate_from="title", include_time=True)
        name, path, args, kwargs = field.deconstruct()

        assert "include_time" in kwargs
        assert kwargs["include_time"] is True

    def test_deconstruct_includes_uniqueness_when_custom(self) -> None:
        """Test deconstruct includes uniqueness when not default."""
        field = LocalizedUniqueSlugField(populate_from="title", uniqueness=["en"])
        name, path, args, kwargs = field.deconstruct()

        assert "uniqueness" in kwargs
        assert kwargs["uniqueness"] == ["en"]

    def test_deconstruct_includes_enabled_when_false(self) -> None:
        """Test deconstruct includes enabled when False."""
        field = LocalizedUniqueSlugField(populate_from="title", enabled=False)
        name, path, args, kwargs = field.deconstruct()

        assert "enabled" in kwargs
        assert kwargs["enabled"] is False

    def test_deconstruct_includes_immutable_when_true(self) -> None:
        """Test deconstruct includes immutable when True."""
        field = LocalizedUniqueSlugField(populate_from="title", immutable=True)
        name, path, args, kwargs = field.deconstruct()

        assert "immutable" in kwargs
        assert kwargs["immutable"] is True


class TestLocalizedUniqueSlugFieldFormfield:
    """Tests for LocalizedUniqueSlugField.formfield."""

    def test_formfield_returns_hidden_input(self) -> None:
        """Test formfield uses HiddenInput widget."""
        field = LocalizedUniqueSlugField(populate_from="title")
        form_field = field.formfield()

        assert isinstance(form_field.widget, forms.HiddenInput)

    def test_formfield_not_required(self) -> None:
        """Test formfield is not required."""
        field = LocalizedUniqueSlugField(populate_from="title")
        form_field = field.formfield()

        assert not form_field.required


@pytest.mark.django_db(transaction=True)
class TestLocalizedUniqueSlugFieldModel:
    """Database tests for LocalizedUniqueSlugField."""

    def test_auto_generates_slug(self) -> None:
        """Test slug is auto-generated from source field."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title"),
            },
            use_slug_retry=True,
        )
        try:
            obj = model.objects.create(title={"en": "Hello World", "nl": "Hallo Wereld"})
            assert obj.slug["en"] == "hello-world"
            assert obj.slug["nl"] == "hallo-wereld"
        finally:
            cleanup_fake_model(model)

    def test_slug_unicode_support(self) -> None:
        """Test slug supports unicode characters."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title"),
            },
            use_slug_retry=True,
        )
        try:
            obj = model.objects.create(title={"en": "Cafe", "de": "Cafe"})
            assert "cafe" in obj.slug["en"].lower()
        finally:
            cleanup_fake_model(model)

    def test_unique_slug_on_conflict(self) -> None:
        """Test unique slugs are generated on conflict."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title"),
            },
            use_slug_retry=True,
        )
        try:
            obj1 = model.objects.create(title={"en": "Test Article"})
            obj2 = model.objects.create(title={"en": "Test Article"})

            assert obj1.slug["en"] == "test-article"
            assert obj2.slug["en"] != obj1.slug["en"]
            assert obj2.slug["en"].startswith("test-article")
        finally:
            cleanup_fake_model(model)

    def test_slug_with_include_time(self) -> None:
        """Test slug with include_time=True."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title", include_time=True),
            },
            use_slug_retry=True,
        )
        try:
            obj = model.objects.create(title={"en": "Test"})
            # Slug should contain a numeric suffix from microseconds
            assert obj.slug["en"].startswith("test-")
            # Should have numbers after the dash
            assert any(c.isdigit() for c in obj.slug["en"])
        finally:
            cleanup_fake_model(model)

    def test_slug_disabled(self) -> None:
        """Test slug is not generated when disabled."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title", enabled=False),
            },
            use_slug_retry=True,
        )
        try:
            obj = model()
            obj.title = {"en": "Test", "nl": "Test"}
            obj.slug = {"en": "custom-slug", "nl": "custom-slug-nl"}
            obj.save()

            assert obj.slug["en"] == "custom-slug"
            assert obj.slug["nl"] == "custom-slug-nl"
        finally:
            cleanup_fake_model(model)

    def test_slug_immutable(self) -> None:
        """Test immutable slug doesn't change on update."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title", immutable=True),
            },
            use_slug_retry=True,
        )
        try:
            obj = model.objects.create(title={"en": "Original Title"})
            original_slug = obj.slug["en"]

            obj.title = {"en": "New Title"}
            obj.save()

            # Slug should remain unchanged
            obj.refresh_from_db()
            assert obj.slug["en"] == original_slug
        finally:
            cleanup_fake_model(model)

    def test_requires_atomic_slug_retry_mixin(self) -> None:
        """Test raises ImproperlyConfigured without mixin."""
        # Create model without mixin
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title"),
            },
            use_slug_retry=False,  # Don't add the mixin
        )
        try:
            with pytest.raises(ImproperlyConfigured):
                model.objects.create(title={"en": "Test"})
        finally:
            cleanup_fake_model(model)

    def test_slug_from_tuple_populate_from(self) -> None:
        """Test slug generated from multiple fields."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "subtitle": LocalizedCharField(blank=True),
                "slug": LocalizedUniqueSlugField(populate_from=("title", "subtitle")),
            },
            use_slug_retry=True,
        )
        try:
            obj = model.objects.create(
                title={"en": "Main Title"},
                subtitle={"en": "Sub Title"},
            )
            assert "main-title" in obj.slug["en"]
            assert "sub-title" in obj.slug["en"]
        finally:
            cleanup_fake_model(model)


class TestAtomicSlugRetryMixin:
    """Tests for AtomicSlugRetryMixin."""

    def test_mixin_has_retries_attribute(self) -> None:
        """Test mixin adds retries attribute."""
        assert hasattr(AtomicSlugRetryMixin, "retries")
        assert AtomicSlugRetryMixin.retries == 0

    @pytest.mark.django_db(transaction=True)
    def test_mixin_retries_on_conflict(self) -> None:
        """Test mixin retries save on slug conflict."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title"),
            },
            use_slug_retry=True,
        )
        try:
            # Create first object
            obj1 = model.objects.create(title={"en": "Test"})

            # Create second object with same title - should succeed with different slug
            obj2 = model.objects.create(title={"en": "Test"})

            assert obj1.slug["en"] != obj2.slug["en"]
        finally:
            cleanup_fake_model(model)

    @pytest.mark.django_db(transaction=True)
    def test_mixin_reraises_non_slug_integrity_error(self) -> None:
        """Test mixin re-raises IntegrityError if not related to slug."""
        from django.db import models as django_models

        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title"),
                "unique_field": django_models.CharField(max_length=100, unique=True),
            },
            use_slug_retry=True,
        )
        try:
            # Create first object
            model.objects.create(
                title={"en": "Test"}, unique_field="duplicate"
            )

            # Try to create second with duplicate unique_field (not slug)
            with pytest.raises(IntegrityError) as exc_info:
                model.objects.create(
                    title={"en": "Different Title"}, unique_field="duplicate"
                )

            # Should re-raise the IntegrityError since it's not about slug
            assert "unique_field" in str(exc_info.value) or "UNIQUE" in str(exc_info.value)
        finally:
            cleanup_fake_model(model)

    @pytest.mark.django_db(transaction=True)
    def test_mixin_initializes_retries_if_missing(self) -> None:
        """Test mixin initializes retries attribute if not present on instance."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title"),
            },
            use_slug_retry=True,
        )
        try:
            obj = model(title={"en": "Test"})
            # The instance initially doesn't have a retries instance attribute
            # (only the class has it). The save method checks hasattr and initializes it.
            assert not hasattr(obj, "__dict__") or "retries" not in obj.__dict__

            # Save should initialize retries on the instance
            obj.save()
            # After save, the instance should have retries set
            assert obj.retries == 0
        finally:
            cleanup_fake_model(model)
