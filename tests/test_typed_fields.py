"""Tests for typed localized fields (Integer, Float, Boolean)."""

from django.db.utils import IntegrityError
from django.utils import translation

import pytest
from i18n_fields.fields import (
    LocalizedBooleanField,
    LocalizedFloatField,
    LocalizedIntegerField,
)
from i18n_fields.forms import (
    LocalizedBooleanFieldForm,
    LocalizedFloatFieldForm,
    LocalizedIntegerFieldForm,
)
from i18n_fields.value import (
    LocalizedBooleanValue,
    LocalizedFloatValue,
    LocalizedIntegerValue,
)

from .fake_model import cleanup_fake_model, get_fake_model


class TestLocalizedIntegerField:
    """Tests for LocalizedIntegerField."""

    def test_attr_class_is_integer_value(self) -> None:
        """Test LocalizedIntegerField uses LocalizedIntegerValue."""
        field = LocalizedIntegerField()
        assert field.attr_class == LocalizedIntegerValue

    def test_from_db_value_dict(self) -> None:
        """Test from_db_value with dictionary of integers."""
        field = LocalizedIntegerField()
        input_data = {"en": 42, "nl": 100}
        value = field.from_db_value(input_data, None, None)

        assert isinstance(value, LocalizedIntegerValue)
        assert value.get("en") == 42
        assert value.get("nl") == 100

    def test_from_db_value_string(self) -> None:
        """Test from_db_value with string (from key transform)."""
        field = LocalizedIntegerField()
        value = field.from_db_value("123", None, None)
        assert value == 123

    def test_from_db_value_invalid_string(self) -> None:
        """Test from_db_value with invalid string returns None."""
        field = LocalizedIntegerField()
        value = field.from_db_value("not a number", None, None)
        assert value is None

    def test_from_db_value_float_becomes_int(self) -> None:
        """Test from_db_value converts float to int."""
        field = LocalizedIntegerField()
        value = field.from_db_value(3.7, None, None)
        assert value == 3
        assert isinstance(value, int)

    def test_to_python(self) -> None:
        """Test to_python returns LocalizedIntegerValue."""
        field = LocalizedIntegerField()
        value = field.to_python({"en": 42})
        assert isinstance(value, LocalizedIntegerValue)
        assert value.get("en") == 42

    def test_get_prep_value_validates_integers(self) -> None:
        """Test get_prep_value validates integer values."""
        field = LocalizedIntegerField()
        value = LocalizedIntegerValue({"en": "not a number"})

        with pytest.raises(IntegrityError) as exc_info:
            field.get_prep_value(value)
        assert "integer" in str(exc_info.value).lower()

    def test_get_prep_value_converts_strings(self) -> None:
        """Test get_prep_value converts valid string to int."""
        field = LocalizedIntegerField()
        value = LocalizedIntegerValue({"en": 42})
        result = field.get_prep_value(value)

        assert result["en"] == 42
        assert isinstance(result["en"], int)

    def test_formfield_returns_integer_form(self) -> None:
        """Test formfield returns LocalizedIntegerFieldForm."""
        field = LocalizedIntegerField()
        form_field = field.formfield()
        assert isinstance(form_field, LocalizedIntegerFieldForm)

    def test_get_transform(self) -> None:
        """Test get_transform returns integer-casting transform."""
        field = LocalizedIntegerField()
        transform = field.get_transform("en")
        assert transform is not None


@pytest.mark.django_db(transaction=True)
class TestLocalizedIntegerFieldModel:
    """Database tests for LocalizedIntegerField."""

    def test_create_with_integers(self) -> None:
        """Test creating model with integer values."""
        model = get_fake_model({"count": LocalizedIntegerField(blank=True, null=True)})
        try:
            obj = model.objects.create(count={"en": 100, "nl": 50})
            assert obj.count["en"] == 100
            assert obj.count["nl"] == 50
        finally:
            cleanup_fake_model(model)

    def test_null_values(self) -> None:
        """Test null values are handled correctly."""
        model = get_fake_model({"count": LocalizedIntegerField(blank=True, null=True)})
        try:
            obj = model.objects.create(count={"en": None})
            assert obj.count.get("en") is None
        finally:
            cleanup_fake_model(model)

    def test_translate_returns_int(self) -> None:
        """Test translate returns integer."""
        model = get_fake_model({"count": LocalizedIntegerField(blank=True, null=True)})
        try:
            obj = model.objects.create(count={"en": 42})
            with translation.override("en"):
                assert obj.count.translate() == 42
                assert isinstance(obj.count.translate(), int)
        finally:
            cleanup_fake_model(model)


class TestLocalizedFloatField:
    """Tests for LocalizedFloatField."""

    def test_attr_class_is_float_value(self) -> None:
        """Test LocalizedFloatField uses LocalizedFloatValue."""
        field = LocalizedFloatField()
        assert field.attr_class == LocalizedFloatValue

    def test_from_db_value_dict(self) -> None:
        """Test from_db_value with dictionary of floats."""
        field = LocalizedFloatField()
        input_data = {"en": 3.14, "nl": 2.71}
        value = field.from_db_value(input_data, None, None)

        assert isinstance(value, LocalizedFloatValue)
        assert value.get("en") == 3.14
        assert value.get("nl") == 2.71

    def test_from_db_value_string(self) -> None:
        """Test from_db_value with string (from key transform)."""
        field = LocalizedFloatField()
        value = field.from_db_value("3.14", None, None)
        assert value == 3.14

    def test_from_db_value_invalid_string(self) -> None:
        """Test from_db_value with invalid string returns None."""
        field = LocalizedFloatField()
        value = field.from_db_value("not a number", None, None)
        assert value is None

    def test_from_db_value_int_becomes_float(self) -> None:
        """Test from_db_value converts int to float."""
        field = LocalizedFloatField()
        value = field.from_db_value(42, None, None)
        assert value == 42.0
        assert isinstance(value, float)

    def test_to_python(self) -> None:
        """Test to_python returns LocalizedFloatValue."""
        field = LocalizedFloatField()
        value = field.to_python({"en": 3.14})
        assert isinstance(value, LocalizedFloatValue)
        assert value.get("en") == 3.14

    def test_get_prep_value_validates_floats(self) -> None:
        """Test get_prep_value validates float values."""
        field = LocalizedFloatField()
        value = LocalizedFloatValue({"en": "not a number"})

        with pytest.raises(IntegrityError) as exc_info:
            field.get_prep_value(value)
        assert "float" in str(exc_info.value).lower()

    def test_formfield_returns_float_form(self) -> None:
        """Test formfield returns LocalizedFloatFieldForm."""
        field = LocalizedFloatField()
        form_field = field.formfield()
        assert isinstance(form_field, LocalizedFloatFieldForm)


@pytest.mark.django_db(transaction=True)
class TestLocalizedFloatFieldModel:
    """Database tests for LocalizedFloatField."""

    def test_create_with_floats(self) -> None:
        """Test creating model with float values."""
        model = get_fake_model({"rating": LocalizedFloatField(blank=True, null=True)})
        try:
            obj = model.objects.create(rating={"en": 4.5, "nl": 4.2})
            assert obj.rating["en"] == 4.5
            assert obj.rating["nl"] == 4.2
        finally:
            cleanup_fake_model(model)

    def test_null_values(self) -> None:
        """Test null values are handled correctly."""
        model = get_fake_model({"rating": LocalizedFloatField(blank=True, null=True)})
        try:
            obj = model.objects.create(rating={"en": None})
            assert obj.rating.get("en") is None
        finally:
            cleanup_fake_model(model)

    def test_translate_returns_float(self) -> None:
        """Test translate returns float."""
        model = get_fake_model({"rating": LocalizedFloatField(blank=True, null=True)})
        try:
            obj = model.objects.create(rating={"en": 3.14})
            with translation.override("en"):
                assert obj.rating.translate() == 3.14
                assert isinstance(obj.rating.translate(), float)
        finally:
            cleanup_fake_model(model)


class TestLocalizedBooleanField:
    """Tests for LocalizedBooleanField."""

    def test_attr_class_is_boolean_value(self) -> None:
        """Test LocalizedBooleanField uses LocalizedBooleanValue."""
        field = LocalizedBooleanField()
        assert field.attr_class == LocalizedBooleanValue

    def test_from_db_value_dict(self) -> None:
        """Test from_db_value with dictionary of booleans."""
        field = LocalizedBooleanField()
        input_data = {"en": True, "nl": False}
        value = field.from_db_value(input_data, None, None)

        assert isinstance(value, LocalizedBooleanValue)
        assert value.get("en") is True
        assert value.get("nl") is False

    def test_from_db_value_string_true(self) -> None:
        """Test from_db_value with 'true' string."""
        field = LocalizedBooleanField()
        value = field.from_db_value("true", None, None)
        assert value is True

    def test_from_db_value_string_false(self) -> None:
        """Test from_db_value with 'false' string."""
        field = LocalizedBooleanField()
        value = field.from_db_value("false", None, None)
        assert value is False

    def test_from_db_value_bool(self) -> None:
        """Test from_db_value with boolean."""
        field = LocalizedBooleanField()
        assert field.from_db_value(True, None, None) is True
        assert field.from_db_value(False, None, None) is False

    def test_to_python(self) -> None:
        """Test to_python returns LocalizedBooleanValue."""
        field = LocalizedBooleanField()
        value = field.to_python({"en": True})
        assert isinstance(value, LocalizedBooleanValue)
        assert value.get("en") is True

    def test_get_prep_value_validates_booleans(self) -> None:
        """Test get_prep_value validates boolean values."""
        field = LocalizedBooleanField()
        value = LocalizedBooleanValue({"en": "not a boolean"})

        with pytest.raises(IntegrityError) as exc_info:
            field.get_prep_value(value)
        assert "boolean" in str(exc_info.value).lower()

    def test_get_prep_value_converts_strings(self) -> None:
        """Test get_prep_value converts 'true'/'false' strings."""
        field = LocalizedBooleanField()
        value = LocalizedBooleanValue({"en": True, "nl": False})
        result = field.get_prep_value(value)

        assert result["en"] is True
        assert result["nl"] is False

    def test_formfield_returns_boolean_form(self) -> None:
        """Test formfield returns LocalizedBooleanFieldForm."""
        field = LocalizedBooleanField()
        form_field = field.formfield()
        assert isinstance(form_field, LocalizedBooleanFieldForm)


@pytest.mark.django_db(transaction=True)
class TestLocalizedBooleanFieldModel:
    """Database tests for LocalizedBooleanField."""

    def test_create_with_booleans(self) -> None:
        """Test creating model with boolean values."""
        model = get_fake_model({"active": LocalizedBooleanField(blank=True, null=True)})
        try:
            obj = model.objects.create(active={"en": True, "nl": False})
            assert obj.active["en"] is True
            assert obj.active["nl"] is False
        finally:
            cleanup_fake_model(model)

    def test_null_values(self) -> None:
        """Test null values are handled correctly."""
        model = get_fake_model({"active": LocalizedBooleanField(blank=True, null=True)})
        try:
            obj = model.objects.create(active={"en": None})
            assert obj.active.get("en") is None
        finally:
            cleanup_fake_model(model)

    def test_translate_returns_bool(self) -> None:
        """Test translate returns boolean."""
        model = get_fake_model({"active": LocalizedBooleanField(blank=True, null=True)})
        try:
            obj = model.objects.create(active={"en": True})
            with translation.override("en"):
                assert obj.active.translate() is True
                assert isinstance(obj.active.translate(), bool)
        finally:
            cleanup_fake_model(model)
