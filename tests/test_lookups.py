"""Tests for query lookups on localized fields."""

from django.utils import translation

import pytest
from i18n_fields.fields import LocalizedCharField

from .fake_model import cleanup_fake_model, get_fake_model


@pytest.fixture
def category_model():
    """Create a model with localized name field."""
    model = get_fake_model({"name": LocalizedCharField()})
    yield model
    cleanup_fake_model(model)


@pytest.fixture
def categories(category_model):
    """Create test categories."""
    return [
        category_model.objects.create(
            name={"en": "Technology", "nl": "Technologie", "de": "Technologie"}
        ),
        category_model.objects.create(
            name={"en": "Science", "nl": "Wetenschap", "de": "Wissenschaft"}
        ),
        category_model.objects.create(
            name={"en": "Sports", "nl": "Sport", "de": "Sport"}
        ),
    ]


@pytest.mark.django_db(transaction=True)
class TestExactLookup:
    """Tests for exact and iexact lookups."""

    def test_exact_lookup(self, category_model, categories) -> None:
        """Test exact lookup on localized field."""
        with translation.override("en"):
            result = category_model.objects.filter(name="Technology")
            assert result.count() == 1
            assert result.first().name["en"] == "Technology"

    def test_exact_lookup_different_language(self, category_model, categories) -> None:
        """Test exact lookup uses active language."""
        with translation.override("nl"):
            result = category_model.objects.filter(name="Wetenschap")
            assert result.count() == 1
            assert result.first().name["en"] == "Science"

    def test_iexact_lookup(self, category_model, categories) -> None:
        """Test case-insensitive exact lookup."""
        with translation.override("en"):
            result = category_model.objects.filter(name__iexact="technology")
            assert result.count() == 1
            assert result.first().name["en"] == "Technology"


@pytest.mark.django_db(transaction=True)
class TestContainsLookup:
    """Tests for contains and icontains lookups."""

    def test_contains_lookup(self, category_model, categories) -> None:
        """Test contains lookup."""
        with translation.override("en"):
            result = category_model.objects.filter(name__contains="Tech")
            assert result.count() == 1
            assert result.first().name["en"] == "Technology"

    def test_icontains_lookup(self, category_model, categories) -> None:
        """Test case-insensitive contains lookup."""
        with translation.override("en"):
            result = category_model.objects.filter(name__icontains="tech")
            assert result.count() == 1


@pytest.mark.django_db(transaction=True)
class TestStartsWithLookup:
    """Tests for startswith and istartswith lookups."""

    def test_startswith_lookup(self, category_model, categories) -> None:
        """Test startswith lookup."""
        with translation.override("en"):
            result = category_model.objects.filter(name__startswith="Sc")
            assert result.count() == 1
            assert result.first().name["en"] == "Science"

    def test_istartswith_lookup(self, category_model, categories) -> None:
        """Test case-insensitive startswith lookup."""
        with translation.override("en"):
            result = category_model.objects.filter(name__istartswith="sc")
            assert result.count() == 1


@pytest.mark.django_db(transaction=True)
class TestEndsWithLookup:
    """Tests for endswith and iendswith lookups."""

    def test_endswith_lookup(self, category_model, categories) -> None:
        """Test endswith lookup."""
        with translation.override("en"):
            result = category_model.objects.filter(name__endswith="ogy")
            assert result.count() == 1
            assert result.first().name["en"] == "Technology"

    def test_iendswith_lookup(self, category_model, categories) -> None:
        """Test case-insensitive endswith lookup."""
        with translation.override("en"):
            result = category_model.objects.filter(name__iendswith="OGY")
            assert result.count() == 1


@pytest.mark.django_db(transaction=True)
class TestInLookup:
    """Tests for in lookup."""

    def test_in_lookup(self, category_model, categories) -> None:
        """Test in lookup."""
        with translation.override("en"):
            result = category_model.objects.filter(
                name__in=["Technology", "Science"]
            )
            assert result.count() == 2


@pytest.mark.django_db(transaction=True)
class TestIsNullLookup:
    """Tests for isnull lookup."""

    def test_isnull_lookup(self, category_model) -> None:
        """Test isnull lookup."""
        # Create one with null name for a specific language
        category_model.objects.create(name={"en": "Test", "nl": ""})

        with translation.override("en"):
            result = category_model.objects.filter(name__isnull=False)
            assert result.count() >= 1


@pytest.mark.django_db(transaction=True)
class TestRegexLookup:
    """Tests for regex and iregex lookups."""

    def test_regex_lookup(self, category_model, categories) -> None:
        """Test regex lookup."""
        with translation.override("en"):
            result = category_model.objects.filter(name__regex=r"^Tech.*")
            assert result.count() == 1
            assert result.first().name["en"] == "Technology"

    def test_iregex_lookup(self, category_model, categories) -> None:
        """Test case-insensitive regex lookup."""
        with translation.override("en"):
            result = category_model.objects.filter(name__iregex=r"^tech.*")
            assert result.count() == 1


@pytest.mark.django_db(transaction=True)
class TestActiveRefLookup:
    """Tests for active_ref transform/lookup."""

    def test_active_ref_in_values(self, category_model, categories) -> None:
        """Test active_ref in values()."""
        with translation.override("en"):
            result = category_model.objects.values("name__active_ref").first()
            assert result["name__active_ref"] in ["Technology", "Science", "Sports"]

    def test_active_ref_changes_with_language(self, category_model, categories) -> None:
        """Test active_ref returns value in active language."""
        obj = categories[0]  # Technology / Technologie

        with translation.override("en"):
            result = category_model.objects.filter(pk=obj.pk).values(
                "name__active_ref"
            ).first()
            assert result["name__active_ref"] == "Technology"

        with translation.override("nl"):
            result = category_model.objects.filter(pk=obj.pk).values(
                "name__active_ref"
            ).first()
            assert result["name__active_ref"] == "Technologie"


@pytest.mark.django_db(transaction=True)
class TestTranslatedRefLookup:
    """Tests for translated_ref transform/lookup with fallback."""

    def test_translated_ref_in_values(self, category_model) -> None:
        """Test translated_ref in values()."""
        # Create item with only English value
        obj = category_model.objects.create(name={"en": "English Only"})

        with translation.override("en"):
            result = category_model.objects.filter(pk=obj.pk).values(
                "name__translated_ref"
            ).first()
            assert result["name__translated_ref"] == "English Only"

    def test_translated_ref_uses_fallback(self, category_model) -> None:
        """Test translated_ref falls back when value missing."""
        # Create item with only English value
        obj = category_model.objects.create(name={"en": "English Only"})

        # nl falls back to en
        with translation.override("nl"):
            result = category_model.objects.filter(pk=obj.pk).values(
                "name__translated_ref"
            ).first()
            # Should fall back to English
            assert result["name__translated_ref"] == "English Only"


@pytest.mark.django_db(transaction=True)
class TestLanguageSpecificLookup:
    """Tests for looking up specific language via key transform."""

    def test_key_transform_lookup(self, category_model, categories) -> None:
        """Test filtering on specific language key."""
        # Filter on English value regardless of active language
        with translation.override("nl"):
            result = category_model.objects.filter(name__en="Technology")
            assert result.count() == 1

    def test_key_transform_different_language(self, category_model, categories) -> None:
        """Test filtering on non-active language key."""
        # Filter on Dutch value while active language is English
        with translation.override("en"):
            result = category_model.objects.filter(name__nl="Wetenschap")
            assert result.count() == 1
            assert result.first().name["en"] == "Science"
