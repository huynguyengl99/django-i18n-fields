"""Tests for LocalizedField and LocalizedCharField."""

import json

from django.conf import settings
from django.db import models
from django.db.utils import IntegrityError

import pytest
from i18n_fields.fields import LocalizedCharField, LocalizedField, LocalizedTextField
from i18n_fields.forms import LocalizedCharFieldForm, LocalizedFieldForm
from i18n_fields.value import LocalizedStringValue, LocalizedValue

from .data import get_init_values
from .fake_model import cleanup_fake_model, get_fake_model


class TestLocalizedFieldInit:
    """Tests for LocalizedField.__init__."""

    def test_blank_true_means_no_required(self) -> None:
        """Test that blank=True sets required to empty list."""
        field = LocalizedField(blank=True)
        assert field.required == []

    def test_blank_false_means_primary_required(self) -> None:
        """Test that blank=False requires primary language."""
        field = LocalizedField(blank=False)
        assert field.required == [settings.LANGUAGE_CODE]

    def test_required_true_means_all_required(self) -> None:
        """Test that required=True requires all languages."""
        field = LocalizedField(required=True)
        assert field.required == [lang for lang, _ in settings.LANGUAGES]

    def test_required_false_means_none_required(self) -> None:
        """Test that required=False requires no languages."""
        field = LocalizedField(required=False)
        assert field.required == []

    def test_required_list(self) -> None:
        """Test that required can be a list of languages."""
        field = LocalizedField(required=["en", "nl"])
        assert field.required == ["en", "nl"]


class TestLocalizedFieldConversion:
    """Tests for LocalizedField conversion methods."""

    def test_from_db_value_dict(self) -> None:
        """Test from_db_value with dictionary."""
        input_data = get_init_values()
        field = LocalizedField()
        value = field.from_db_value(input_data, None, None)

        assert isinstance(value, LocalizedValue)
        for lang_code, _ in settings.LANGUAGES:
            assert getattr(value, lang_code) == input_data[lang_code]

    def test_from_db_value_none(self) -> None:
        """Test from_db_value with None."""
        field = LocalizedField()
        value = field.from_db_value(None, None, None)
        assert value is None

    def test_from_db_value_json_string(self) -> None:
        """Test from_db_value with JSON string (SQLite)."""
        input_data = get_init_values()
        json_str = json.dumps(input_data)
        field = LocalizedField()
        value = field.from_db_value(json_str, None, None)

        assert isinstance(value, LocalizedValue)
        for lang_code, _ in settings.LANGUAGES:
            assert value.get(lang_code) == input_data[lang_code]

    def test_from_db_value_non_json_string(self) -> None:
        """Test from_db_value with plain string (from KeyTransform)."""
        field = LocalizedField()
        value = field.from_db_value("plain value", None, None)
        assert value == "plain value"

    def test_from_db_value_list(self) -> None:
        """Test from_db_value with list (from aggregation)."""
        input_data = [get_init_values(), get_init_values()]
        field = LocalizedField()
        value = field.from_db_value(input_data, None, None)

        assert isinstance(value, list)
        assert len(value) == 2
        assert all(isinstance(v, LocalizedValue) for v in value)

    def test_to_python_dict(self) -> None:
        """Test to_python with dictionary."""
        input_data = get_init_values()
        field = LocalizedField()
        value = field.to_python(input_data)

        assert isinstance(value, LocalizedValue)
        for language, expected in input_data.items():
            assert value.get(language) == expected

    def test_to_python_string(self) -> None:
        """Test to_python with plain string."""
        field = LocalizedField()
        value = field.to_python("my value")
        assert value.get(settings.LANGUAGE_CODE) == "my value"

    def test_to_python_json_string(self) -> None:
        """Test to_python with JSON string."""
        input_data = get_init_values()
        json_str = json.dumps(input_data)
        field = LocalizedField()
        value = field.to_python(json_str)

        assert isinstance(value, LocalizedValue)
        for language, expected in input_data.items():
            assert value.get(language) == expected

    def test_to_python_none(self) -> None:
        """Test to_python with None returns empty LocalizedValue."""
        field = LocalizedField()
        value = field.to_python(None)

        assert isinstance(value, LocalizedValue)
        for lang_code, _ in settings.LANGUAGES:
            assert value.get(lang_code) is None

    def test_get_prep_value_localized_value(self) -> None:
        """Test get_prep_value with LocalizedValue."""
        input_data = get_init_values()
        localized_value = LocalizedValue(input_data)
        field = LocalizedField()
        output = field.get_prep_value(localized_value)

        assert isinstance(output, dict)
        for language, expected in input_data.items():
            assert output.get(language) == expected

    def test_get_prep_value_none(self) -> None:
        """Test get_prep_value with None."""
        field = LocalizedField()
        output = field.get_prep_value(None)
        assert output is None

    def test_get_prep_value_non_localized_value(self) -> None:
        """Test get_prep_value with non-LocalizedValue returns None."""
        field = LocalizedField()
        output = field.get_prep_value(["not", "a", "value"])
        assert output is None


class TestLocalizedFieldClean:
    """Tests for LocalizedField.clean method."""

    def test_clean_returns_none_for_empty_with_null_true(self) -> None:
        """Test clean returns None for all-null value when null=True."""
        field = LocalizedField(null=True)
        value = LocalizedValue()
        assert field.clean(value) is None

    def test_clean_returns_value_when_not_empty(self) -> None:
        """Test clean returns value when not all null."""
        field = LocalizedField()
        value = LocalizedValue({settings.LANGUAGE_CODE: "test"})
        result = field.clean(value)
        assert result is not None
        assert result.get(settings.LANGUAGE_CODE) == "test"

    def test_clean_returns_none_for_none(self) -> None:
        """Test clean returns None for None input."""
        field = LocalizedField()
        assert field.clean(None) is None


class TestLocalizedFieldValidation:
    """Tests for LocalizedField.validate method."""

    def test_validate_skips_when_null_true(self) -> None:
        """Test validate doesn't raise when null=True."""
        field = LocalizedField(null=True, required=["en"])
        value = LocalizedValue()
        field.validate(value)  # Should not raise

    def test_validate_raises_for_missing_required(self) -> None:
        """Test validate raises IntegrityError for missing required."""
        field = LocalizedField(null=False, required=["en"])
        value = LocalizedValue()

        with pytest.raises(IntegrityError) as exc_info:
            field.validate(value)
        assert "en" in str(exc_info.value)


class TestLocalizedFieldFormfield:
    """Tests for LocalizedField.formfield method."""

    def test_formfield_returns_localized_form(self) -> None:
        """Test formfield returns LocalizedFieldForm."""
        field = LocalizedField()
        form_field = field.formfield()
        assert isinstance(form_field, LocalizedFieldForm)

    def test_formfield_optional_when_blank(self) -> None:
        """Test formfield is optional when blank=True."""
        field = LocalizedField(blank=True, required=[])
        form_field = field.formfield()
        assert not form_field.required

    def test_formfield_required_when_not_blank(self) -> None:
        """Test formfield is required when blank=False."""
        field = LocalizedField(blank=False, required=[])
        form_field = field.formfield()
        assert form_field.required

    def test_formfield_language_fields_required(self) -> None:
        """Test specific language fields are required."""
        required_langs = ["en", "nl"]
        field = LocalizedField(blank=False, required=required_langs)
        form_field = field.formfield()

        for sub_field in form_field.fields:
            if sub_field.label in required_langs:
                assert sub_field.required
            else:
                assert not sub_field.required


class TestLocalizedFieldDeconstruct:
    """Tests for LocalizedField.deconstruct method."""

    def test_deconstruct_with_required(self) -> None:
        """Test deconstruct includes required in kwargs."""
        field = LocalizedField(required=["en", "nl"])
        name, path, args, kwargs = field.deconstruct()

        assert "required" in kwargs
        assert kwargs["required"] == ["en", "nl"]

    def test_deconstruct_without_required(self) -> None:
        """Test deconstruct omits required when empty."""
        field = LocalizedField(blank=True)
        name, path, args, kwargs = field.deconstruct()

        # required should not be in kwargs when empty
        assert "required" not in kwargs


@pytest.mark.django_db(transaction=True)
class TestLocalizedFieldModel:
    """Tests for LocalizedField with actual model."""

    def test_create_with_dict(self) -> None:
        """Test creating model with dict value."""
        model = get_fake_model({"title": LocalizedField()})
        try:
            input_data = get_init_values()
            obj = model.objects.create(title=input_data)
            assert obj.title.get("en") == input_data["en"]
        finally:
            cleanup_fake_model(model)

    def test_create_with_string(self) -> None:
        """Test creating model with string sets active language."""
        model = get_fake_model({"title": LocalizedField()})
        try:
            obj = model.objects.create(title="test value")
            # String assignment through descriptor sets current language
            assert isinstance(obj.title, LocalizedValue)
        finally:
            cleanup_fake_model(model)

    def test_required_all_validation(self) -> None:
        """Test required=True validates all languages."""
        model = get_fake_model({"title": LocalizedField(required=True)})
        try:
            with pytest.raises(IntegrityError):
                model.objects.create(title={"en": "only english"})
        finally:
            cleanup_fake_model(model)

    def test_required_some_validation(self) -> None:
        """Test required list validates specific languages."""
        model = get_fake_model({"title": LocalizedField(required=["en", "nl"])})
        try:
            with pytest.raises(IntegrityError):
                model.objects.create(title={"en": "english"})  # Missing nl
        finally:
            cleanup_fake_model(model)

    def test_descriptor_with_custom_primary_key(self) -> None:
        """Test descriptor works with user-defined primary key."""
        model = get_fake_model({
            "slug": models.SlugField(primary_key=True),
            "title": LocalizedField(),
        })
        try:
            obj = model.objects.create(slug="test", title="test value")
            assert isinstance(obj.title, LocalizedValue)
        finally:
            cleanup_fake_model(model)


class TestLocalizedCharField:
    """Tests for LocalizedCharField."""

    def test_attr_class_is_string_value(self) -> None:
        """Test LocalizedCharField uses LocalizedStringValue."""
        field = LocalizedCharField()
        assert field.attr_class == LocalizedStringValue

    def test_formfield_returns_char_form(self) -> None:
        """Test formfield returns LocalizedCharFieldForm."""
        field = LocalizedCharField()
        form_field = field.formfield()
        assert isinstance(form_field, LocalizedCharFieldForm)


class TestLocalizedTextField:
    """Tests for LocalizedTextField."""

    def test_inherits_from_char_field(self) -> None:
        """Test LocalizedTextField inherits from LocalizedCharField."""
        assert issubclass(LocalizedTextField, LocalizedCharField)

    def test_attr_class_is_string_value(self) -> None:
        """Test LocalizedTextField uses LocalizedStringValue."""
        field = LocalizedTextField()
        assert field.attr_class == LocalizedStringValue

    def test_formfield_returns_text_form(self) -> None:
        """Test formfield returns LocalizedTextFieldForm."""
        from i18n_fields.forms import LocalizedTextFieldForm

        field = LocalizedTextField()
        form_field = field.formfield()
        assert isinstance(form_field, LocalizedTextFieldForm)


@pytest.mark.django_db(transaction=True)
class TestLocalizedValueDescriptor:
    """Tests for LocalizedValueDescriptor."""

    def test_descriptor_refresh_from_db_when_not_in_dict(self) -> None:
        """Test descriptor calls refresh_from_db when field not in __dict__."""
        model = get_fake_model({"title": LocalizedCharField()})
        try:
            obj = model.objects.create(title={"en": "Test", "nl": "Test NL"})
            obj_id = obj.pk

            # Get a fresh instance
            obj2 = model.objects.get(pk=obj_id)
            # Clear the field from __dict__ to force refresh_from_db path
            if "title" in obj2.__dict__:
                del obj2.__dict__["title"]

            # Accessing the field should trigger refresh_from_db
            value = obj2.title
            assert isinstance(value, LocalizedValue)
            assert value.get("en") == "Test"
        finally:
            cleanup_fake_model(model)

    def test_descriptor_handles_json_string(self) -> None:
        """Test descriptor converts JSON string to LocalizedValue."""
        model = get_fake_model({"title": LocalizedCharField()})
        try:
            obj = model()
            # Simulate database returning JSON string
            obj.__dict__["title"] = '{"en": "From JSON", "nl": "Van JSON"}'

            # Accessing should parse JSON
            value = obj.title
            assert isinstance(value, LocalizedValue)
            assert value.get("en") == "From JSON"
            assert value.get("nl") == "Van JSON"
        finally:
            cleanup_fake_model(model)

    def test_descriptor_handles_invalid_json_string(self) -> None:
        """Test descriptor handles invalid JSON by creating LocalizedValue with string."""
        model = get_fake_model({"title": LocalizedCharField()})
        try:
            obj = model()
            # Simulate database returning non-JSON string
            obj.__dict__["title"] = "not valid json {"

            # Accessing should create LocalizedValue with default language
            value = obj.title
            assert isinstance(value, LocalizedValue)
            assert value.get(settings.LANGUAGE_CODE) == "not valid json {"
        finally:
            cleanup_fake_model(model)

    def test_descriptor_converts_dict_to_localized_value(self) -> None:
        """Test descriptor converts plain dict to LocalizedValue."""
        model = get_fake_model({"title": LocalizedCharField()})
        try:
            obj = model()
            # Simulate database returning plain dict
            obj.__dict__["title"] = {"en": "Dict Value", "nl": "Dict Waarde"}

            # Accessing should convert to LocalizedValue
            value = obj.title
            assert isinstance(value, LocalizedValue)
            assert value.get("en") == "Dict Value"
        finally:
            cleanup_fake_model(model)
