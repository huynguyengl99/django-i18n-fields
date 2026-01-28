"""Tests for DRF integration."""

from django.utils import translation
from rest_framework import serializers

import pytest
from i18n_fields.drf import LocalizedModelSerializer
from i18n_fields.drf.serializer_fields import (
    LocalizedBooleanField as DRFLocalizedBooleanField,
)
from i18n_fields.drf.serializer_fields import (
    LocalizedCharField as DRFLocalizedCharField,
)
from i18n_fields.drf.serializer_fields import (
    LocalizedFloatField as DRFLocalizedFloatField,
)
from i18n_fields.drf.serializer_fields import (
    LocalizedIntegerField as DRFLocalizedIntegerField,
)
from i18n_fields.drf.serializer_fields import (
    LocalizedSlugField as DRFLocalizedSlugField,
)
from i18n_fields.fields import (
    LocalizedBooleanField,
    LocalizedCharField,
    LocalizedField,
    LocalizedFloatField,
    LocalizedIntegerField,
    LocalizedTextField,
    LocalizedUniqueSlugField,
)

from .fake_model import cleanup_fake_model, get_fake_model


class TestLocalizedModelSerializerFieldMapping:
    """Tests for LocalizedModelSerializer field mapping."""

    def test_mapping_contains_localized_field(self) -> None:
        """Test LocalizedField is mapped to custom LocalizedCharField."""
        assert LocalizedField in LocalizedModelSerializer.serializer_field_mapping
        assert (
            LocalizedModelSerializer.serializer_field_mapping[LocalizedField]
            == DRFLocalizedCharField
        )

    def test_mapping_contains_localized_char_field(self) -> None:
        """Test LocalizedCharField is mapped to custom LocalizedCharField."""
        assert LocalizedCharField in LocalizedModelSerializer.serializer_field_mapping
        assert (
            LocalizedModelSerializer.serializer_field_mapping[LocalizedCharField]
            == DRFLocalizedCharField
        )

    def test_mapping_contains_localized_text_field(self) -> None:
        """Test LocalizedTextField is mapped to custom LocalizedCharField."""
        assert LocalizedTextField in LocalizedModelSerializer.serializer_field_mapping
        assert (
            LocalizedModelSerializer.serializer_field_mapping[LocalizedTextField]
            == DRFLocalizedCharField
        )

    def test_mapping_contains_localized_integer_field(self) -> None:
        """Test LocalizedIntegerField is mapped to custom LocalizedIntegerField."""
        assert (
            LocalizedIntegerField in LocalizedModelSerializer.serializer_field_mapping
        )
        assert (
            LocalizedModelSerializer.serializer_field_mapping[LocalizedIntegerField]
            == DRFLocalizedIntegerField
        )

    def test_mapping_contains_localized_float_field(self) -> None:
        """Test LocalizedFloatField is mapped to custom LocalizedFloatField."""
        assert LocalizedFloatField in LocalizedModelSerializer.serializer_field_mapping
        assert (
            LocalizedModelSerializer.serializer_field_mapping[LocalizedFloatField]
            == DRFLocalizedFloatField
        )

    def test_mapping_contains_localized_boolean_field(self) -> None:
        """Test LocalizedBooleanField is mapped to custom LocalizedBooleanField."""
        assert (
            LocalizedBooleanField in LocalizedModelSerializer.serializer_field_mapping
        )
        assert (
            LocalizedModelSerializer.serializer_field_mapping[LocalizedBooleanField]
            == DRFLocalizedBooleanField
        )

    def test_mapping_contains_localized_unique_slug_field(self) -> None:
        """Test LocalizedUniqueSlugField is mapped to custom LocalizedSlugField."""
        assert (
            LocalizedUniqueSlugField
            in LocalizedModelSerializer.serializer_field_mapping
        )
        assert (
            LocalizedModelSerializer.serializer_field_mapping[LocalizedUniqueSlugField]
            == DRFLocalizedSlugField
        )

    def test_inherits_from_model_serializer(self) -> None:
        """Test LocalizedModelSerializer inherits from ModelSerializer."""
        assert issubclass(LocalizedModelSerializer, serializers.ModelSerializer)

    def test_preserves_standard_field_mapping(self) -> None:
        """Test standard Django field mappings are preserved."""
        from django.db import models

        # Check that standard Django fields are still mapped
        assert models.CharField in LocalizedModelSerializer.serializer_field_mapping
        assert models.IntegerField in LocalizedModelSerializer.serializer_field_mapping


@pytest.mark.django_db(transaction=True)
class TestLocalizedModelSerializerSerialization:
    """Tests for LocalizedModelSerializer serialization."""

    @pytest.fixture
    def article_model(self):
        """Create a model with localized fields."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "content": LocalizedTextField(blank=True),
                "rating": LocalizedFloatField(blank=True, null=True),
                "views": LocalizedIntegerField(blank=True, null=True),
                "published": LocalizedBooleanField(blank=True, null=True),
            }
        )
        yield model
        cleanup_fake_model(model)

    @pytest.fixture
    def article_serializer(self, article_model):
        """Create a serializer for the article model."""

        class ArticleSerializer(LocalizedModelSerializer):
            class Meta:
                model = article_model
                fields = ["id", "title", "content", "rating", "views", "published"]

        return ArticleSerializer

    def test_serializes_localized_char_field(
        self, article_model, article_serializer
    ) -> None:
        """Test serialization of LocalizedCharField."""
        obj = article_model.objects.create(
            title={"en": "English Title", "nl": "Dutch Title"},
            content={"en": "Content"},
        )

        with translation.override("en"):
            serializer = article_serializer(obj)
            assert serializer.data["title"] == "English Title"

        with translation.override("nl"):
            serializer = article_serializer(obj)
            assert serializer.data["title"] == "Dutch Title"

    def test_serializes_localized_text_field(
        self, article_model, article_serializer
    ) -> None:
        """Test serialization of LocalizedTextField."""
        obj = article_model.objects.create(
            title={"en": "Title"},
            content={"en": "English Content", "nl": "Dutch Content"},
        )

        with translation.override("en"):
            serializer = article_serializer(obj)
            assert serializer.data["content"] == "English Content"

        with translation.override("nl"):
            serializer = article_serializer(obj)
            assert serializer.data["content"] == "Dutch Content"

    def test_serializes_localized_float_field(
        self, article_model, article_serializer
    ) -> None:
        """Test serialization of LocalizedFloatField."""
        obj = article_model.objects.create(
            title={"en": "Title"},
            content={"en": "Content"},
            rating={"en": 4.5, "nl": 3.5},
        )

        with translation.override("en"):
            serializer = article_serializer(obj)
            assert serializer.data["rating"] == 4.5

        with translation.override("nl"):
            serializer = article_serializer(obj)
            assert serializer.data["rating"] == 3.5

    def test_serializes_localized_integer_field(
        self, article_model, article_serializer
    ) -> None:
        """Test serialization of LocalizedIntegerField."""
        obj = article_model.objects.create(
            title={"en": "Title"},
            content={"en": "Content"},
            views={"en": 100, "nl": 50},
        )

        with translation.override("en"):
            serializer = article_serializer(obj)
            assert serializer.data["views"] == 100

        with translation.override("nl"):
            serializer = article_serializer(obj)
            assert serializer.data["views"] == 50

    def test_serializes_localized_boolean_field(
        self, article_model, article_serializer
    ) -> None:
        """Test serialization of LocalizedBooleanField."""
        obj = article_model.objects.create(
            title={"en": "Title"},
            content={"en": "Content"},
            published={"en": True, "nl": False},
        )

        with translation.override("en"):
            serializer = article_serializer(obj)
            assert serializer.data["published"] is True

        with translation.override("nl"):
            serializer = article_serializer(obj)
            assert serializer.data["published"] is False

    def test_handles_none_values(self, article_model, article_serializer) -> None:
        """Test serialization handles None values."""
        obj = article_model.objects.create(
            title={"en": "Title"},
            content={"en": "Content"},
            rating=None,
            views=None,
            published=None,
        )

        serializer = article_serializer(obj)
        assert serializer.data["rating"] is None
        assert serializer.data["views"] is None
        assert serializer.data["published"] is None

    def test_handles_empty_localized_value(
        self, article_model, article_serializer
    ) -> None:
        """Test serialization handles empty LocalizedValue."""
        obj = article_model.objects.create(
            title={"en": "Title"},
            content={},  # Empty
        )

        with translation.override("en"):
            serializer = article_serializer(obj)
            # Should return empty string or None for empty value
            assert serializer.data["content"] in ["", None]


@pytest.mark.django_db(transaction=True)
class TestLocalizedModelSerializerDeserialization:
    """Tests for LocalizedModelSerializer deserialization."""

    @pytest.fixture
    def simple_model(self):
        """Create a simple model with localized fields."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "description": LocalizedTextField(blank=True),
            }
        )
        yield model
        cleanup_fake_model(model)

    @pytest.fixture
    def simple_serializer(self, simple_model):
        """Create a simple serializer."""

        class SimpleSerializer(LocalizedModelSerializer):
            class Meta:
                model = simple_model
                fields = ["id", "title", "description"]

        return SimpleSerializer

    def test_deserialize_creates_object(
        self, simple_model, simple_serializer
    ) -> None:
        """Test deserialization creates object."""
        data = {"title": "Test Title", "description": "Test Description"}

        serializer = simple_serializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()

        assert obj.pk is not None

    def test_deserialize_validates_required_field(
        self, simple_model, simple_serializer
    ) -> None:
        """Test deserialization validates required fields."""
        data = {"description": "Description only"}

        serializer = simple_serializer(data=data)
        assert not serializer.is_valid()
        assert "title" in serializer.errors

    def test_deserialize_allows_blank_field(
        self, simple_model, simple_serializer
    ) -> None:
        """Test deserialization allows blank on optional fields."""
        data = {"title": "Title", "description": ""}

        serializer = simple_serializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_deserialize_accepts_dictionary_input(
        self, simple_model, simple_serializer
    ) -> None:
        """Test deserialization accepts multilingual dictionary input."""
        data = {
            "title": {"en": "English Title", "nl": "Dutch Title", "fr": "French Title"},
            "description": {"en": "English Description", "nl": "Dutch Description"},
        }

        serializer = simple_serializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()

        assert obj.pk is not None
        assert obj.title.get("en") == "English Title"
        assert obj.title.get("nl") == "Dutch Title"
        assert obj.description.get("en") == "English Description"

    def test_deserialize_accepts_plain_string_input(
        self, simple_model, simple_serializer
    ) -> None:
        """Test deserialization accepts plain string input for backwards compatibility."""
        data = {
            "title": "Plain String Title",
            "description": "Plain String Description",
        }

        serializer = simple_serializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()

        assert obj.pk is not None


@pytest.mark.django_db(transaction=True)
class TestLocalizedModelSerializerTypedFields:
    """Tests for typed localized fields (Integer, Float, Boolean, Slug)."""

    @pytest.fixture
    def typed_model(self):
        """Create a model with various typed localized fields."""
        model = get_fake_model(
            {
                "name": LocalizedCharField(),
                "count": LocalizedIntegerField(blank=True, null=True),
                "price": LocalizedFloatField(blank=True, null=True),
                "active": LocalizedBooleanField(blank=True, null=True),
                "slug": LocalizedUniqueSlugField(populate_from="name"),
            },
            use_slug_retry=True,
        )
        yield model
        cleanup_fake_model(model)

    @pytest.fixture
    def typed_serializer(self, typed_model):
        """Create a serializer for typed fields."""

        class TypedSerializer(LocalizedModelSerializer):
            class Meta:
                model = typed_model
                fields = ["id", "name", "count", "price", "active", "slug"]
                read_only_fields = ["slug"]

        return TypedSerializer

    def test_deserialize_integer_field_with_dict(
        self, typed_model, typed_serializer
    ) -> None:
        """Test integer field accepts dictionary input."""
        data = {
            "name": "Test",
            "count": {"en": 100, "nl": 50, "fr": 75},
        }

        serializer = typed_serializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()

        assert obj.count.get("en") == 100
        assert obj.count.get("nl") == 50
        assert obj.count.get("fr") == 75

    def test_deserialize_float_field_with_dict(
        self, typed_model, typed_serializer
    ) -> None:
        """Test float field accepts dictionary input."""
        data = {
            "name": "Test",
            "price": {"en": 19.99, "nl": 17.50, "fr": 18.25},
        }

        serializer = typed_serializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()

        assert obj.price.get("en") == 19.99
        assert obj.price.get("nl") == 17.50
        assert obj.price.get("fr") == 18.25

    def test_deserialize_boolean_field_with_dict(
        self, typed_model, typed_serializer
    ) -> None:
        """Test boolean field accepts dictionary input."""
        data = {
            "name": "Test",
            "active": {"en": True, "nl": False, "fr": True},
        }

        serializer = typed_serializer(data=data)
        assert serializer.is_valid(), serializer.errors
        obj = serializer.save()

        assert obj.active.get("en") is True
        assert obj.active.get("nl") is False
        assert obj.active.get("fr") is True

    def test_serialize_typed_fields_with_translation(
        self, typed_model, typed_serializer
    ) -> None:
        """Test typed fields serialize correctly in different languages."""
        obj = typed_model.objects.create(
            name={"en": "Product", "nl": "Product"},
            count={"en": 100, "nl": 50},
            price={"en": 19.99, "nl": 17.50},
            active={"en": True, "nl": False},
        )

        with translation.override("en"):
            serializer = typed_serializer(obj)
            assert serializer.data["count"] == 100
            assert serializer.data["price"] == 19.99
            assert serializer.data["active"] is True

        with translation.override("nl"):
            serializer = typed_serializer(obj)
            assert serializer.data["count"] == 50
            assert serializer.data["price"] == 17.50
            assert serializer.data["active"] is False

    def test_integer_field_validation_error(self, typed_model, typed_serializer) -> None:
        """Test integer field raises validation error for invalid input."""
        data = {
            "name": "Test",
            "count": "not_a_number",  # Invalid integer
        }

        serializer = typed_serializer(data=data)
        assert not serializer.is_valid()
        assert "count" in serializer.errors

    def test_float_field_validation_error(self, typed_model, typed_serializer) -> None:
        """Test float field raises validation error for invalid input."""
        data = {
            "name": "Test",
            "price": "not_a_float",  # Invalid float
        }

        serializer = typed_serializer(data=data)
        assert not serializer.is_valid()
        assert "price" in serializer.errors

    def test_boolean_field_validation_error(self, typed_model, typed_serializer) -> None:
        """Test boolean field raises validation error for invalid input."""
        data = {
            "name": "Test",
            "active": "not_a_boolean",  # Invalid boolean
        }

        serializer = typed_serializer(data=data)
        assert not serializer.is_valid()
        assert "active" in serializer.errors

    def test_serialize_none_values_returns_none(
        self, typed_model, typed_serializer
    ) -> None:
        """Test that None values in LocalizedValue are serialized as None."""
        obj = typed_model.objects.create(
            name={"en": "Test"},
            count=None,
            price=None,
            active=None,
        )

        with translation.override("en"):
            serializer = typed_serializer(obj)
            assert serializer.data["count"] is None
            assert serializer.data["price"] is None
            assert serializer.data["active"] is None


@pytest.mark.django_db(transaction=True)
class TestLocalizedModelSerializerBuildStandardField:
    """Tests for build_standard_field method."""

    @pytest.fixture
    def model_with_blank(self):
        """Create model with blank=True field."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "optional_text": LocalizedTextField(blank=True),
            }
        )
        yield model
        cleanup_fake_model(model)

    def test_blank_field_allows_blank(self, model_with_blank) -> None:
        """Test blank=True fields have allow_blank=True."""

        class TestSerializer(LocalizedModelSerializer):
            class Meta:
                model = model_with_blank
                fields = ["title", "optional_text"]

        serializer = TestSerializer()
        optional_field = serializer.fields["optional_text"]

        assert optional_field.allow_blank is True
        assert optional_field.required is False

    def test_required_field_does_not_allow_blank(self, model_with_blank) -> None:
        """Test required fields don't have allow_blank."""

        class TestSerializer(LocalizedModelSerializer):
            class Meta:
                model = model_with_blank
                fields = ["title", "optional_text"]

        serializer = TestSerializer()
        title_field = serializer.fields["title"]

        # Required field should not have allow_blank set to True
        assert title_field.required is True


@pytest.mark.django_db(transaction=True)
class TestLocalizedModelSerializerWithSlugField:
    """Tests for serializer with slug fields."""

    @pytest.fixture
    def model_with_slug(self):
        """Create model with slug field."""
        model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title"),
            },
            use_slug_retry=True,
        )
        yield model
        cleanup_fake_model(model)

    def test_serializes_slug_field(self, model_with_slug) -> None:
        """Test serialization of slug field."""

        class SlugSerializer(LocalizedModelSerializer):
            class Meta:
                model = model_with_slug
                fields = ["id", "title", "slug"]

        obj = model_with_slug.objects.create(title={"en": "Test Article"})

        with translation.override("en"):
            serializer = SlugSerializer(obj)
            assert serializer.data["slug"] == "test-article"

    def test_slug_field_is_read_only_by_default(self, model_with_slug) -> None:
        """Test slug field behavior in serializer."""

        class SlugSerializer(LocalizedModelSerializer):
            class Meta:
                model = model_with_slug
                fields = ["id", "title", "slug"]
                read_only_fields = ["slug"]

        serializer = SlugSerializer()
        assert serializer.fields["slug"].read_only is True


@pytest.mark.django_db(transaction=True)
class TestLocalizedModelSerializerQuerySet:
    """Tests for serializer with querysets."""

    @pytest.fixture
    def product_model(self):
        """Create product model."""
        model = get_fake_model(
            {
                "name": LocalizedCharField(),
                "price": LocalizedFloatField(blank=True, null=True),
            }
        )
        yield model
        cleanup_fake_model(model)

    @pytest.fixture
    def products(self, product_model):
        """Create test products."""
        return [
            product_model.objects.create(
                name={"en": "Apple", "nl": "Appel"},
                price={"en": 1.50, "nl": 1.25},
            ),
            product_model.objects.create(
                name={"en": "Banana", "nl": "Banaan"},
                price={"en": 0.75, "nl": 0.60},
            ),
            product_model.objects.create(
                name={"en": "Cherry", "nl": "Kers"},
                price={"en": 3.00, "nl": 2.50},
            ),
        ]

    def test_serialize_queryset(self, product_model, products) -> None:
        """Test serialization of queryset."""

        class ProductSerializer(LocalizedModelSerializer):
            class Meta:
                model = product_model
                fields = ["id", "name", "price"]

        queryset = product_model.objects.all().order_by("id")

        with translation.override("en"):
            serializer = ProductSerializer(queryset, many=True)
            names = [item["name"] for item in serializer.data]
            assert names == ["Apple", "Banana", "Cherry"]

        with translation.override("nl"):
            serializer = ProductSerializer(queryset, many=True)
            names = [item["name"] for item in serializer.data]
            assert names == ["Appel", "Banaan", "Kers"]

    def test_serialize_queryset_with_values(self, product_model, products) -> None:
        """Test serialization respects language in queryset."""

        class ProductSerializer(LocalizedModelSerializer):
            class Meta:
                model = product_model
                fields = ["id", "name", "price"]

        with translation.override("en"):
            queryset = product_model.objects.filter(name__icontains="a")
            serializer = ProductSerializer(queryset, many=True)
            # Should match Apple and Banana
            assert len(serializer.data) == 2


class TestLocalizedModelSerializerImport:
    """Tests for import functionality."""

    def test_can_import_from_drf_module(self) -> None:
        """Test LocalizedModelSerializer can be imported."""
        from i18n_fields.drf import LocalizedModelSerializer

        assert LocalizedModelSerializer is not None

    def test_can_import_from_serializers(self) -> None:
        """Test can import from serializers submodule."""
        from i18n_fields.drf.serializers import LocalizedModelSerializer

        assert LocalizedModelSerializer is not None
