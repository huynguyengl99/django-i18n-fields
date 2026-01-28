"""Tests for i18n_fields localized fields."""

from django.utils import translation

import pytest
from i18n_fields import (
    L,
    LocalizedRef,
    LocalizedStringValue,
)

from articles.models import Article, Category


@pytest.mark.django_db
class TestLocalizedCharField:
    """Tests for LocalizedCharField."""

    def test_create_with_dict(self):
        """Test creating a model with a dict value."""
        category = Category.objects.create(
            name={"en": "Technology", "nl": "Technologie", "fr": "Technologie"}
        )
        assert category.name["en"] == "Technology"
        assert category.name["nl"] == "Technologie"

    def test_create_with_localized_value(self):
        """Test creating a model with a LocalizedStringValue."""
        name = LocalizedStringValue({"en": "Science", "de": "Wissenschaft"})
        category = Category.objects.create(name=name)
        assert category.name["en"] == "Science"
        assert category.name["de"] == "Wissenschaft"

    def test_translate_returns_current_language(self):
        """Test that translate() returns value in current language."""
        category = Category.objects.create(
            name={"en": "Sports", "nl": "Sport", "fr": "Sports"}
        )
        with translation.override("en"):
            assert category.name.translate() == "Sports"
        with translation.override("nl"):
            assert category.name.translate() == "Sport"

    def test_translate_with_fallback(self):
        """Test that translate() falls back when value is missing."""
        category = Category.objects.create(name={"en": "News"})
        # nl falls back to en per settings
        with translation.override("nl"):
            assert category.name.translate() == "News"

    def test_str_returns_translated_value(self):
        """Test that str() returns the translated value."""
        category = Category.objects.create(name={"en": "Business"})
        with translation.override("en"):
            assert str(category.name) == "Business"


@pytest.mark.django_db
class TestLocalizedTextField:
    """Tests for LocalizedTextField."""

    def test_create_with_long_text(self):
        """Test creating a model with long text content."""
        content = {
            "en": "This is a long article content in English.",
            "nl": "Dit is een lange artikel inhoud in het Nederlands.",
        }
        article = Article.objects.create(
            title={"en": "Test Article"},
            content=content,
        )
        assert article.content["en"] == content["en"]
        assert article.content["nl"] == content["nl"]


@pytest.mark.django_db
class TestLocalizedTypedFields:
    """Tests for LocalizedIntegerField, LocalizedFloatField, LocalizedBooleanField."""

    def test_integer_field(self):
        """Test LocalizedIntegerField stores integers."""
        article = Article.objects.create(
            title={"en": "Test"},
            view_count={"en": 100, "nl": 50},
        )
        assert article.view_count["en"] == 100
        assert article.view_count["nl"] == 50

    def test_float_field(self):
        """Test LocalizedFloatField stores floats."""
        article = Article.objects.create(
            title={"en": "Test"},
            rating={"en": 4.5, "nl": 4.2},
        )
        assert article.rating["en"] == 4.5
        assert article.rating["nl"] == 4.2

    def test_boolean_field(self):
        """Test LocalizedBooleanField stores booleans."""
        article = Article.objects.create(
            title={"en": "Test"},
            is_featured={"en": True, "nl": False},
        )
        assert article.is_featured["en"] is True
        assert article.is_featured["nl"] is False


@pytest.mark.django_db
class TestLocalizedUniqueSlugField:
    """Tests for LocalizedUniqueSlugField."""

    def test_auto_generates_slug(self):
        """Test that slug is auto-generated from title."""
        article = Article.objects.create(title={"en": "Hello World", "nl": "Hallo Wereld"})
        assert article.slug["en"] == "hello-world"
        assert article.slug["nl"] == "hallo-wereld"

    def test_unique_slug_on_conflict(self):
        """Test that unique slugs are generated on conflict."""
        article1 = Article.objects.create(title={"en": "Test Article"})
        article2 = Article.objects.create(title={"en": "Test Article"})
        assert article1.slug["en"] == "test-article"
        assert article2.slug["en"] != article1.slug["en"]
        assert article2.slug["en"].startswith("test-article")


@pytest.mark.django_db
class TestLocalizedLookups:
    """Tests for query lookups on localized fields."""

    @pytest.fixture
    def categories(self):
        """Create test categories."""
        return [
            Category.objects.create(name={"en": "Technology", "nl": "Technologie"}),
            Category.objects.create(name={"en": "Science", "nl": "Wetenschap"}),
            Category.objects.create(name={"en": "Sports", "nl": "Sport"}),
        ]

    def test_exact_lookup(self, categories):
        """Test exact lookup on localized field."""
        with translation.override("en"):
            result = Category.objects.filter(name="Technology")
            assert result.count() == 1
            assert result.first().name["en"] == "Technology"

    def test_iexact_lookup(self, categories):
        """Test case-insensitive exact lookup."""
        with translation.override("en"):
            result = Category.objects.filter(name__iexact="technology")
            assert result.count() == 1

    def test_contains_lookup(self, categories):
        """Test contains lookup on localized field."""
        with translation.override("en"):
            result = Category.objects.filter(name__contains="Tech")
            assert result.count() == 1

    def test_icontains_lookup(self, categories):
        """Test case-insensitive contains lookup."""
        with translation.override("en"):
            result = Category.objects.filter(name__icontains="tech")
            assert result.count() == 1

    def test_startswith_lookup(self, categories):
        """Test startswith lookup."""
        with translation.override("en"):
            result = Category.objects.filter(name__startswith="Sc")
            assert result.count() == 1
            assert result.first().name["en"] == "Science"

    def test_endswith_lookup(self, categories):
        """Test endswith lookup."""
        with translation.override("en"):
            result = Category.objects.filter(name__endswith="ogy")
            assert result.count() == 1

    def test_lookup_in_different_language(self, categories):
        """Test lookup works in different language."""
        with translation.override("nl"):
            result = Category.objects.filter(name="Wetenschap")
            assert result.count() == 1
            assert result.first().name["en"] == "Science"


@pytest.mark.django_db
class TestLocalizedExpressions:
    """Tests for LocalizedRef expression."""

    def test_localized_ref_annotation(self):
        """Test using LocalizedRef in annotation."""
        Category.objects.create(name={"en": "Tech", "nl": "Technologie"})

        with translation.override("en"):
            result = Category.objects.annotate(name_text=LocalizedRef("name")).first()
            assert result.name_text == "Tech"

        with translation.override("nl"):
            result = Category.objects.annotate(name_text=LocalizedRef("name")).first()
            assert result.name_text == "Technologie"

    def test_localized_ref_specific_language(self):
        """Test LocalizedRef with specific language."""
        Category.objects.create(name={"en": "Tech", "nl": "Technologie"})

        # Always get English regardless of current language
        with translation.override("nl"):
            result = Category.objects.annotate(name_en=LocalizedRef("name", "en")).first()
            assert result.name_en == "Tech"

    def test_l_shorthand(self):
        """Test L() shorthand for LocalizedRef."""
        Category.objects.create(name={"en": "Tech"})

        with translation.override("en"):
            result = Category.objects.annotate(name_text=L("name")).first()
            assert result.name_text == "Tech"

    def test_order_by_localized_ref(self):
        """Test ordering by LocalizedRef."""
        Category.objects.create(name={"en": "Zebra"})
        Category.objects.create(name={"en": "Apple"})
        Category.objects.create(name={"en": "Mango"})

        with translation.override("en"):
            result = list(
                Category.objects.annotate(name_text=L("name")).order_by("name_text").values_list("name_text", flat=True)
            )
            assert result == ["Apple", "Mango", "Zebra"]

    def test_values_with_localized_ref(self):
        """Test using LocalizedRef in values()."""
        Category.objects.create(name={"en": "Tech", "nl": "Technologie"})

        with translation.override("en"):
            result = Category.objects.annotate(name_text=L("name")).values("id", "name_text").first()
            assert result["name_text"] == "Tech"
