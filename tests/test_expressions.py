"""Tests for query expressions (LocalizedRef, L)."""

from django.utils import translation

import pytest
from i18n_fields.expressions import L, LocalizedRef
from i18n_fields.fields import LocalizedCharField

from .fake_model import cleanup_fake_model, get_fake_model


@pytest.fixture
def product_model():
    """Create a model with localized name field."""
    model = get_fake_model({"name": LocalizedCharField()})
    yield model
    cleanup_fake_model(model)


@pytest.fixture
def products(product_model):
    """Create test products."""
    return [
        product_model.objects.create(
            name={"en": "Apple", "nl": "Appel", "de": "Apfel"}
        ),
        product_model.objects.create(
            name={"en": "Banana", "nl": "Banaan", "de": "Banane"}
        ),
        product_model.objects.create(
            name={"en": "Cherry", "nl": "Kers", "de": "Kirsche"}
        ),
    ]


@pytest.mark.django_db(transaction=True)
class TestLocalizedRef:
    """Tests for LocalizedRef expression."""

    def test_annotation_with_active_language(self, product_model, products) -> None:
        """Test LocalizedRef annotation uses active language."""
        with translation.override("en"):
            result = product_model.objects.annotate(
                name_text=LocalizedRef("name")
            ).first()
            assert result.name_text in ["Apple", "Banana", "Cherry"]

    def test_annotation_changes_with_language(self, product_model, products) -> None:
        """Test LocalizedRef returns different value per language."""
        obj = products[0]  # Apple / Appel / Apfel

        with translation.override("en"):
            result = product_model.objects.filter(pk=obj.pk).annotate(
                name_text=LocalizedRef("name")
            ).first()
            assert result.name_text == "Apple"

        with translation.override("nl"):
            result = product_model.objects.filter(pk=obj.pk).annotate(
                name_text=LocalizedRef("name")
            ).first()
            assert result.name_text == "Appel"

        with translation.override("de"):
            result = product_model.objects.filter(pk=obj.pk).annotate(
                name_text=LocalizedRef("name")
            ).first()
            assert result.name_text == "Apfel"

    def test_annotation_with_specific_language(self, product_model, products) -> None:
        """Test LocalizedRef with explicit language parameter."""
        obj = products[0]  # Apple / Appel / Apfel

        # Request English value while in Dutch context
        with translation.override("nl"):
            result = product_model.objects.filter(pk=obj.pk).annotate(
                name_en=LocalizedRef("name", "en")
            ).first()
            assert result.name_en == "Apple"

    def test_values_with_localized_ref(self, product_model, products) -> None:
        """Test using LocalizedRef in values()."""
        with translation.override("en"):
            result = product_model.objects.annotate(
                name_text=LocalizedRef("name")
            ).values("id", "name_text").first()
            assert "name_text" in result
            assert result["name_text"] in ["Apple", "Banana", "Cherry"]

    def test_order_by_localized_ref(self, product_model, products) -> None:
        """Test ordering by LocalizedRef."""
        with translation.override("en"):
            result = list(
                product_model.objects.annotate(
                    name_text=LocalizedRef("name")
                ).order_by("name_text").values_list("name_text", flat=True)
            )
            assert result == ["Apple", "Banana", "Cherry"]

        with translation.override("nl"):
            result = list(
                product_model.objects.annotate(
                    name_text=LocalizedRef("name")
                ).order_by("name_text").values_list("name_text", flat=True)
            )
            assert result == ["Appel", "Banaan", "Kers"]

    def test_order_by_descending(self, product_model, products) -> None:
        """Test ordering by LocalizedRef descending."""
        with translation.override("en"):
            result = list(
                product_model.objects.annotate(
                    name_text=LocalizedRef("name")
                ).order_by("-name_text").values_list("name_text", flat=True)
            )
            assert result == ["Cherry", "Banana", "Apple"]

    def test_filter_on_annotation(self, product_model, products) -> None:
        """Test filtering on LocalizedRef annotation."""
        with translation.override("en"):
            result = product_model.objects.annotate(
                name_text=LocalizedRef("name")
            ).filter(name_text="Apple")
            assert result.count() == 1
            assert result.first().name["en"] == "Apple"


@pytest.mark.django_db(transaction=True)
class TestLShorthand:
    """Tests for L() shorthand function."""

    def test_l_returns_localized_ref(self) -> None:
        """Test L() returns LocalizedRef instance."""
        ref = L("name")
        assert isinstance(ref, LocalizedRef)

    def test_l_with_language(self) -> None:
        """Test L() with explicit language."""
        ref = L("name", "en")
        assert isinstance(ref, LocalizedRef)

    def test_l_annotation(self, product_model, products) -> None:
        """Test L() in annotation."""
        with translation.override("en"):
            result = product_model.objects.annotate(
                name_text=L("name")
            ).first()
            assert result.name_text in ["Apple", "Banana", "Cherry"]

    def test_l_with_specific_language(self, product_model, products) -> None:
        """Test L() with specific language."""
        obj = products[0]  # Apple

        with translation.override("nl"):
            result = product_model.objects.filter(pk=obj.pk).annotate(
                name_en=L("name", "en")
            ).first()
            assert result.name_en == "Apple"

    def test_l_in_values(self, product_model, products) -> None:
        """Test L() in values()."""
        with translation.override("en"):
            result = product_model.objects.annotate(
                name_text=L("name")
            ).values("id", "name_text").first()
            assert result["name_text"] in ["Apple", "Banana", "Cherry"]


@pytest.mark.django_db(transaction=True)
class TestLocalizedRefWithMultipleFields:
    """Tests for LocalizedRef with multiple localized fields."""

    def test_multiple_annotations(self, product_model) -> None:
        """Test multiple LocalizedRef annotations."""
        # Create model with multiple localized fields
        model = get_fake_model({
            "name": LocalizedCharField(),
            "description": LocalizedCharField(blank=True),
        })
        try:
            obj = model.objects.create(
                name={"en": "Product", "nl": "Product NL"},
                description={"en": "Description", "nl": "Beschrijving"},
            )

            with translation.override("en"):
                result = model.objects.filter(pk=obj.pk).annotate(
                    name_text=L("name"),
                    desc_text=L("description"),
                ).first()
                assert result.name_text == "Product"
                assert result.desc_text == "Description"

            with translation.override("nl"):
                result = model.objects.filter(pk=obj.pk).annotate(
                    name_text=L("name"),
                    desc_text=L("description"),
                ).first()
                assert result.name_text == "Product NL"
                assert result.desc_text == "Beschrijving"
        finally:
            cleanup_fake_model(model)
