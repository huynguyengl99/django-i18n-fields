"""Tests for DRF integration using Django TestCase."""

from django.test import TestCase, TransactionTestCase
from django.utils import translation
from rest_framework import serializers

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


class TestLocalizedModelSerializerFieldMapping(TestCase):
    """Tests for LocalizedModelSerializer field mapping."""

    def test_mapping_contains_localized_field(self):
        """Test LocalizedField is mapped to custom LocalizedCharField."""
        self.assertIn(LocalizedField, LocalizedModelSerializer.serializer_field_mapping)
        self.assertEqual(
            LocalizedModelSerializer.serializer_field_mapping[LocalizedField],
            DRFLocalizedCharField,
        )

    def test_mapping_contains_localized_char_field(self):
        """Test LocalizedCharField is mapped to custom LocalizedCharField."""
        self.assertIn(LocalizedCharField, LocalizedModelSerializer.serializer_field_mapping)
        self.assertEqual(
            LocalizedModelSerializer.serializer_field_mapping[LocalizedCharField],
            DRFLocalizedCharField,
        )

    def test_mapping_contains_localized_text_field(self):
        """Test LocalizedTextField is mapped to custom LocalizedCharField."""
        self.assertIn(LocalizedTextField, LocalizedModelSerializer.serializer_field_mapping)
        self.assertEqual(
            LocalizedModelSerializer.serializer_field_mapping[LocalizedTextField],
            DRFLocalizedCharField,
        )

    def test_mapping_contains_localized_integer_field(self):
        """Test LocalizedIntegerField is mapped to custom LocalizedIntegerField."""
        self.assertIn(
            LocalizedIntegerField, LocalizedModelSerializer.serializer_field_mapping
        )
        self.assertEqual(
            LocalizedModelSerializer.serializer_field_mapping[LocalizedIntegerField],
            DRFLocalizedIntegerField,
        )

    def test_mapping_contains_localized_float_field(self):
        """Test LocalizedFloatField is mapped to custom LocalizedFloatField."""
        self.assertIn(LocalizedFloatField, LocalizedModelSerializer.serializer_field_mapping)
        self.assertEqual(
            LocalizedModelSerializer.serializer_field_mapping[LocalizedFloatField],
            DRFLocalizedFloatField,
        )

    def test_mapping_contains_localized_boolean_field(self):
        """Test LocalizedBooleanField is mapped to custom LocalizedBooleanField."""
        self.assertIn(
            LocalizedBooleanField, LocalizedModelSerializer.serializer_field_mapping
        )
        self.assertEqual(
            LocalizedModelSerializer.serializer_field_mapping[LocalizedBooleanField],
            DRFLocalizedBooleanField,
        )

    def test_mapping_contains_localized_unique_slug_field(self):
        """Test LocalizedUniqueSlugField is mapped to custom LocalizedSlugField."""
        self.assertIn(
            LocalizedUniqueSlugField,
            LocalizedModelSerializer.serializer_field_mapping,
        )
        self.assertEqual(
            LocalizedModelSerializer.serializer_field_mapping[LocalizedUniqueSlugField],
            DRFLocalizedSlugField,
        )

    def test_inherits_from_model_serializer(self):
        """Test LocalizedModelSerializer inherits from ModelSerializer."""
        self.assertTrue(issubclass(LocalizedModelSerializer, serializers.ModelSerializer))

    def test_preserves_standard_field_mapping(self):
        """Test standard Django field mappings are preserved."""
        from django.db import models

        # Check that standard Django fields are still mapped
        self.assertIn(models.CharField, LocalizedModelSerializer.serializer_field_mapping)
        self.assertIn(models.IntegerField, LocalizedModelSerializer.serializer_field_mapping)


class TestLocalizedModelSerializerSerialization(TransactionTestCase):
    """Tests for LocalizedModelSerializer serialization."""

    def setUp(self):
        """Create test model and serializer."""
        self.article_model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "content": LocalizedTextField(blank=True),
                "rating": LocalizedFloatField(blank=True, null=True),
                "views": LocalizedIntegerField(blank=True, null=True),
                "published": LocalizedBooleanField(blank=True, null=True),
            }
        )

        class ArticleSerializer(LocalizedModelSerializer):
            class Meta:
                model = self.article_model
                fields = ["id", "title", "content", "rating", "views", "published"]

        self.article_serializer = ArticleSerializer

    def tearDown(self):
        """Clean up test model."""
        cleanup_fake_model(self.article_model)

    def test_serializes_localized_char_field(self):
        """Test serialization of LocalizedCharField."""
        obj = self.article_model.objects.create(
            title={"en": "English Title", "nl": "Dutch Title"},
            content={"en": "Content"},
        )

        with translation.override("en"):
            serializer = self.article_serializer(obj)
            self.assertEqual(serializer.data["title"], "English Title")

        with translation.override("nl"):
            serializer = self.article_serializer(obj)
            self.assertEqual(serializer.data["title"], "Dutch Title")

    def test_serializes_localized_text_field(self):
        """Test serialization of LocalizedTextField."""
        obj = self.article_model.objects.create(
            title={"en": "Title"},
            content={"en": "English Content", "nl": "Dutch Content"},
        )

        with translation.override("en"):
            serializer = self.article_serializer(obj)
            self.assertEqual(serializer.data["content"], "English Content")

        with translation.override("nl"):
            serializer = self.article_serializer(obj)
            self.assertEqual(serializer.data["content"], "Dutch Content")

    def test_serializes_localized_float_field(self):
        """Test serialization of LocalizedFloatField."""
        obj = self.article_model.objects.create(
            title={"en": "Title"},
            content={"en": "Content"},
            rating={"en": 4.5, "nl": 3.5},
        )

        with translation.override("en"):
            serializer = self.article_serializer(obj)
            self.assertEqual(serializer.data["rating"], 4.5)

        with translation.override("nl"):
            serializer = self.article_serializer(obj)
            self.assertEqual(serializer.data["rating"], 3.5)

    def test_serializes_localized_integer_field(self):
        """Test serialization of LocalizedIntegerField."""
        obj = self.article_model.objects.create(
            title={"en": "Title"},
            content={"en": "Content"},
            views={"en": 100, "nl": 50},
        )

        with translation.override("en"):
            serializer = self.article_serializer(obj)
            self.assertEqual(serializer.data["views"], 100)

        with translation.override("nl"):
            serializer = self.article_serializer(obj)
            self.assertEqual(serializer.data["views"], 50)

    def test_serializes_localized_boolean_field(self):
        """Test serialization of LocalizedBooleanField."""
        obj = self.article_model.objects.create(
            title={"en": "Title"},
            content={"en": "Content"},
            published={"en": True, "nl": False},
        )

        with translation.override("en"):
            serializer = self.article_serializer(obj)
            self.assertIs(serializer.data["published"], True)

        with translation.override("nl"):
            serializer = self.article_serializer(obj)
            self.assertIs(serializer.data["published"], False)

    def test_handles_none_values(self):
        """Test serialization handles None values."""
        obj = self.article_model.objects.create(
            title={"en": "Title"},
            content={"en": "Content"},
            rating=None,
            views=None,
            published=None,
        )

        serializer = self.article_serializer(obj)
        self.assertIsNone(serializer.data["rating"])
        self.assertIsNone(serializer.data["views"])
        self.assertIsNone(serializer.data["published"])

    def test_handles_empty_localized_value(self):
        """Test serialization handles empty LocalizedValue."""
        obj = self.article_model.objects.create(
            title={"en": "Title"},
            content={},  # Empty
        )

        with translation.override("en"):
            serializer = self.article_serializer(obj)
            # Should return empty string or None for empty value
            self.assertIn(serializer.data["content"], ["", None])


class TestLocalizedModelSerializerDeserialization(TransactionTestCase):
    """Tests for LocalizedModelSerializer deserialization."""

    def setUp(self):
        """Create test model and serializer."""
        self.simple_model = get_fake_model(
            {
                "title": LocalizedCharField(),
                "description": LocalizedTextField(blank=True),
            }
        )

        class SimpleSerializer(LocalizedModelSerializer):
            class Meta:
                model = self.simple_model
                fields = ["id", "title", "description"]

        self.simple_serializer = SimpleSerializer

    def tearDown(self):
        """Clean up test model."""
        cleanup_fake_model(self.simple_model)

    def test_deserialize_creates_object(self):
        """Test deserialization creates object."""
        data = {"title": "Test Title", "description": "Test Description"}

        serializer = self.simple_serializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()

        self.assertIsNotNone(obj.pk)

    def test_deserialize_validates_required_field(self):
        """Test deserialization validates required fields."""
        data = {"description": "Description only"}

        serializer = self.simple_serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_deserialize_allows_blank_field(self):
        """Test deserialization allows blank on optional fields."""
        data = {"title": "Title", "description": ""}

        serializer = self.simple_serializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_deserialize_accepts_dictionary_input(self):
        """Test deserialization accepts multilingual dictionary input."""
        data = {
            "title": {"en": "English Title", "nl": "Dutch Title", "fr": "French Title"},
            "description": {"en": "English Description", "nl": "Dutch Description"},
        }

        serializer = self.simple_serializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()

        self.assertIsNotNone(obj.pk)
        self.assertEqual(obj.title.get("en"), "English Title")
        self.assertEqual(obj.title.get("nl"), "Dutch Title")
        self.assertEqual(obj.description.get("en"), "English Description")

    def test_deserialize_accepts_plain_string_input(self):
        """Test deserialization accepts plain string input for backwards compatibility."""
        data = {
            "title": "Plain String Title",
            "description": "Plain String Description",
        }

        serializer = self.simple_serializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()

        self.assertIsNotNone(obj.pk)


class TestLocalizedModelSerializerTypedFields(TransactionTestCase):
    """Tests for typed localized fields (Integer, Float, Boolean, Slug)."""

    def setUp(self):
        """Create test model with typed fields."""
        self.typed_model = get_fake_model(
            {
                "name": LocalizedCharField(),
                "count": LocalizedIntegerField(blank=True, null=True),
                "price": LocalizedFloatField(blank=True, null=True),
                "active": LocalizedBooleanField(blank=True, null=True),
                "slug": LocalizedUniqueSlugField(populate_from="name"),
            },
            use_slug_retry=True,
        )

        class TypedSerializer(LocalizedModelSerializer):
            class Meta:
                model = self.typed_model
                fields = ["id", "name", "count", "price", "active", "slug"]
                read_only_fields = ["slug"]

        self.typed_serializer = TypedSerializer

    def tearDown(self):
        """Clean up test model."""
        cleanup_fake_model(self.typed_model)

    def test_deserialize_integer_field_with_dict(self):
        """Test integer field accepts dictionary input."""
        data = {
            "name": "Test",
            "count": {"en": 100, "nl": 50, "fr": 75},
        }

        serializer = self.typed_serializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()

        self.assertEqual(obj.count.get("en"), 100)
        self.assertEqual(obj.count.get("nl"), 50)
        self.assertEqual(obj.count.get("fr"), 75)

    def test_deserialize_float_field_with_dict(self):
        """Test float field accepts dictionary input."""
        data = {
            "name": "Test",
            "price": {"en": 19.99, "nl": 17.50, "fr": 18.25},
        }

        serializer = self.typed_serializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()

        self.assertEqual(obj.price.get("en"), 19.99)
        self.assertEqual(obj.price.get("nl"), 17.50)
        self.assertEqual(obj.price.get("fr"), 18.25)

    def test_deserialize_boolean_field_with_dict(self):
        """Test boolean field accepts dictionary input."""
        data = {
            "name": "Test",
            "active": {"en": True, "nl": False, "fr": True},
        }

        serializer = self.typed_serializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()

        self.assertIs(obj.active.get("en"), True)
        self.assertIs(obj.active.get("nl"), False)
        self.assertIs(obj.active.get("fr"), True)

    def test_serialize_typed_fields_with_translation(self):
        """Test typed fields serialize correctly in different languages."""
        obj = self.typed_model.objects.create(
            name={"en": "Product", "nl": "Product"},
            count={"en": 100, "nl": 50},
            price={"en": 19.99, "nl": 17.50},
            active={"en": True, "nl": False},
        )

        with translation.override("en"):
            serializer = self.typed_serializer(obj)
            self.assertEqual(serializer.data["count"], 100)
            self.assertEqual(serializer.data["price"], 19.99)
            self.assertIs(serializer.data["active"], True)

        with translation.override("nl"):
            serializer = self.typed_serializer(obj)
            self.assertEqual(serializer.data["count"], 50)
            self.assertEqual(serializer.data["price"], 17.50)
            self.assertIs(serializer.data["active"], False)

    def test_integer_field_validation_error(self):
        """Test integer field raises validation error for invalid input."""
        data = {
            "name": "Test",
            "count": "not_a_number",  # Invalid integer
        }

        serializer = self.typed_serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("count", serializer.errors)

    def test_float_field_validation_error(self):
        """Test float field raises validation error for invalid input."""
        data = {
            "name": "Test",
            "price": "not_a_float",  # Invalid float
        }

        serializer = self.typed_serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_boolean_field_validation_error(self):
        """Test boolean field raises validation error for invalid input."""
        data = {
            "name": "Test",
            "active": "not_a_boolean",  # Invalid boolean
        }

        serializer = self.typed_serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("active", serializer.errors)

    def test_serialize_none_values_returns_none(self):
        """Test that None values in LocalizedValue are serialized as None."""
        obj = self.typed_model.objects.create(
            name={"en": "Test"},
            count=None,
            price=None,
            active=None,
        )

        with translation.override("en"):
            serializer = self.typed_serializer(obj)
            self.assertIsNone(serializer.data["count"])
            self.assertIsNone(serializer.data["price"])
            self.assertIsNone(serializer.data["active"])


class TestLocalizedModelSerializerBuildStandardField(TransactionTestCase):
    """Tests for build_standard_field method."""

    def setUp(self):
        """Create model with blank field."""
        self.model_with_blank = get_fake_model(
            {
                "title": LocalizedCharField(),
                "optional_text": LocalizedTextField(blank=True),
            }
        )

    def tearDown(self):
        """Clean up test model."""
        cleanup_fake_model(self.model_with_blank)

    def test_blank_field_allows_blank(self):
        """Test blank=True fields have allow_blank=True."""

        class TestSerializer(LocalizedModelSerializer):
            class Meta:
                model = self.model_with_blank
                fields = ["title", "optional_text"]

        serializer = TestSerializer()
        optional_field = serializer.fields["optional_text"]

        self.assertTrue(optional_field.allow_blank)
        self.assertFalse(optional_field.required)

    def test_required_field_does_not_allow_blank(self):
        """Test required fields don't have allow_blank."""

        class TestSerializer(LocalizedModelSerializer):
            class Meta:
                model = self.model_with_blank
                fields = ["title", "optional_text"]

        serializer = TestSerializer()
        title_field = serializer.fields["title"]

        # Required field should not have allow_blank set to True
        self.assertTrue(title_field.required)


class TestLocalizedModelSerializerWithSlugField(TransactionTestCase):
    """Tests for serializer with slug fields."""

    def setUp(self):
        """Create model with slug field."""
        self.model_with_slug = get_fake_model(
            {
                "title": LocalizedCharField(),
                "slug": LocalizedUniqueSlugField(populate_from="title"),
            },
            use_slug_retry=True,
        )

    def tearDown(self):
        """Clean up test model."""
        cleanup_fake_model(self.model_with_slug)

    def test_serializes_slug_field(self):
        """Test serialization of slug field."""

        class SlugSerializer(LocalizedModelSerializer):
            class Meta:
                model = self.model_with_slug
                fields = ["id", "title", "slug"]

        obj = self.model_with_slug.objects.create(title={"en": "Test Article"})

        with translation.override("en"):
            serializer = SlugSerializer(obj)
            self.assertEqual(serializer.data["slug"], "test-article")

    def test_slug_field_is_read_only_by_default(self):
        """Test slug field behavior in serializer."""

        class SlugSerializer(LocalizedModelSerializer):
            class Meta:
                model = self.model_with_slug
                fields = ["id", "title", "slug"]
                read_only_fields = ["slug"]

        serializer = SlugSerializer()
        self.assertTrue(serializer.fields["slug"].read_only)


class TestLocalizedModelSerializerQuerySet(TransactionTestCase):
    """Tests for serializer with querysets."""

    def setUp(self):
        """Create product model and test data."""
        self.product_model = get_fake_model(
            {
                "name": LocalizedCharField(),
                "price": LocalizedFloatField(blank=True, null=True),
            }
        )

        self.products = [
            self.product_model.objects.create(
                name={"en": "Apple", "nl": "Appel"},
                price={"en": 1.50, "nl": 1.25},
            ),
            self.product_model.objects.create(
                name={"en": "Banana", "nl": "Banaan"},
                price={"en": 0.75, "nl": 0.60},
            ),
            self.product_model.objects.create(
                name={"en": "Cherry", "nl": "Kers"},
                price={"en": 3.00, "nl": 2.50},
            ),
        ]

    def tearDown(self):
        """Clean up test model."""
        cleanup_fake_model(self.product_model)

    def test_serialize_queryset(self):
        """Test serialization of queryset."""

        class ProductSerializer(LocalizedModelSerializer):
            class Meta:
                model = self.product_model
                fields = ["id", "name", "price"]

        queryset = self.product_model.objects.all().order_by("id")

        with translation.override("en"):
            serializer = ProductSerializer(queryset, many=True)
            names = [item["name"] for item in serializer.data]
            self.assertEqual(names, ["Apple", "Banana", "Cherry"])

        with translation.override("nl"):
            serializer = ProductSerializer(queryset, many=True)
            names = [item["name"] for item in serializer.data]
            self.assertEqual(names, ["Appel", "Banaan", "Kers"])

    def test_serialize_queryset_with_values(self):
        """Test serialization respects language in queryset."""

        class ProductSerializer(LocalizedModelSerializer):
            class Meta:
                model = self.product_model
                fields = ["id", "name", "price"]

        with translation.override("en"):
            queryset = self.product_model.objects.filter(name__icontains="a")
            serializer = ProductSerializer(queryset, many=True)
            # Should match Apple and Banana
            self.assertEqual(len(serializer.data), 2)


class TestLocalizedModelSerializerImport(TestCase):
    """Tests for import functionality."""

    def test_can_import_from_drf_module(self):
        """Test LocalizedModelSerializer can be imported."""
        from i18n_fields.drf import LocalizedModelSerializer

        self.assertIsNotNone(LocalizedModelSerializer)

    def test_can_import_from_serializers(self):
        """Test can import from serializers submodule."""
        from i18n_fields.drf.serializers import LocalizedModelSerializer

        self.assertIsNotNone(LocalizedModelSerializer)
