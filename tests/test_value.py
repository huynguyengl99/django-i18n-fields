"""Tests for LocalizedValue classes."""

from django.conf import settings
from django.db.models import F
from django.test import override_settings
from django.utils import translation

import pytest
from i18n_fields.value import (
    LocalizedBooleanValue,
    LocalizedFileValue,
    LocalizedFloatValue,
    LocalizedIntegerValue,
    LocalizedNumericValue,
    LocalizedStringValue,
    LocalizedValue,
)

from .data import get_init_values


class TestLocalizedValue:
    """Tests for the LocalizedValue class."""

    def teardown_method(self) -> None:
        """Reset to default language after each test."""
        translation.activate(settings.LANGUAGE_CODE)

    def test_init_with_dict(self) -> None:
        """Test initialization with a dictionary."""
        keys = get_init_values()
        value = LocalizedValue(keys)

        for lang_code, _ in settings.LANGUAGES:
            assert getattr(value, lang_code, None) == keys[lang_code]

    def test_init_default_values(self) -> None:
        """Test initialization with no arguments."""
        value = LocalizedValue()

        for lang_code, _ in settings.LANGUAGES:
            assert getattr(value, lang_code) is None

    def test_init_with_string(self) -> None:
        """Test initialization with a string sets primary language."""
        value = LocalizedValue("test value")
        assert value.get(settings.LANGUAGE_CODE) == "test value"

    def test_init_with_array(self) -> None:
        """Test initialization with an array (from ArrayAgg)."""
        value = LocalizedValue(["my value"])
        assert value.get(settings.LANGUAGE_CODE) == "my value"

    def test_is_empty(self) -> None:
        """Test is_empty() method."""
        value = LocalizedValue()
        assert value.is_empty()

        value.set(settings.LANGUAGE_CODE, "my value")
        assert not value.is_empty()

    def test_get_explicit_language(self) -> None:
        """Test get() with explicit language code."""
        keys = get_init_values()
        value = LocalizedValue(keys)

        for language, expected in keys.items():
            assert value.get(language) == expected

    def test_get_default_language(self) -> None:
        """Test get() without language returns primary language value."""
        keys = get_init_values()
        value = LocalizedValue(keys)

        # get() without args should return primary language value
        assert value.get() == keys[settings.LANGUAGE_CODE]

    def test_get_with_default(self) -> None:
        """Test get() with default value."""
        value = LocalizedValue()
        assert value.get("nonexistent", "default") == "default"
        assert value.get(settings.LANGUAGE_CODE, "default") == "default"

    def test_set(self) -> None:
        """Test set() method."""
        value = LocalizedValue()

        for lang_code, _ in settings.LANGUAGES:
            test_value = f"test_{lang_code}"
            value.set(lang_code, test_value)
            assert value.get(lang_code) == test_value
            assert getattr(value, lang_code) == test_value

    def test_set_returns_self(self) -> None:
        """Test that set() returns self for chaining."""
        value = LocalizedValue()
        result = value.set("en", "test")
        assert result is value

    def test_equality(self) -> None:
        """Test __eq__ operator."""
        a = LocalizedValue({"en": "a", "nl": "b"})
        b = LocalizedValue({"en": "a", "nl": "b"})
        assert a == b

        b.en = "different"
        assert a != b

    def test_equality_with_string(self) -> None:
        """Test equality with string uses __str__."""
        value = LocalizedValue({"en": "hello"})
        with translation.override("en"):
            assert value == "hello"
            assert value != "other"

    def test_translate_active_language(self) -> None:
        """Test translate() returns value in active language."""
        keys = get_init_values()
        value = LocalizedValue(keys)

        for language, expected in keys.items():
            translation.activate(language)
            assert value.translate() == expected

    def test_translate_with_fallback(self) -> None:
        """Test translate() falls back to primary language."""
        value = LocalizedValue({settings.LANGUAGE_CODE: "test_value"})

        other_lang = [lang for lang, _ in settings.LANGUAGES if lang != settings.LANGUAGE_CODE][0]
        translation.activate(other_lang)

        # With fallback configured, should return primary language value
        assert value.translate() == "test_value"

    def test_translate_none_when_empty(self) -> None:
        """Test translate() returns None when no value."""
        value = LocalizedValue()
        assert value.translate() is None

    def test_translate_custom_language(self) -> None:
        """Test translate() with specific language parameter."""
        value = LocalizedValue({"en": "english", "nl": "dutch"})

        with translation.override("de"):
            # Should return "nl" value when explicitly requested
            assert value.translate("nl") == "dutch"

    @override_settings(I18N_FIELDS={"FALLBACKS": {"nl": ["de"]}})
    def test_translate_custom_fallback_chain(self) -> None:
        """Test translate() with custom fallback chain."""
        # Need to reload settings
        from i18n_fields.settings import i18n_fields_settings
        i18n_fields_settings.reload()

        value = LocalizedValue({"en": "english", "de": "german"})

        with translation.override("nl"):
            # nl falls back to de
            assert value.translate() == "german"

        # Reset settings
        i18n_fields_settings.reload()

    def test_str_returns_translated(self) -> None:
        """Test __str__ returns translated value."""
        value = LocalizedValue({"en": "hello"})
        with translation.override("en"):
            assert str(value) == "hello"

    def test_str_returns_empty_when_none(self) -> None:
        """Test __str__ returns empty string when no value."""
        value = LocalizedValue()
        assert str(value) == ""

    def test_deconstruct(self) -> None:
        """Test deconstruct() for migrations."""
        keys = get_init_values()
        value = LocalizedValue(keys)

        path, args, kwargs = value.deconstruct()

        assert "LocalizedValue" in path
        assert args[0] == keys
        assert kwargs == {}

    def test_setattr(self) -> None:
        """Test __setattr__ sets language value."""
        value = LocalizedValue()
        value.en = "english"
        assert value.get("en") == "english"

    def test_repr(self) -> None:
        """Test __repr__ output."""
        value = LocalizedValue({"en": "test"})
        repr_str = repr(value)
        assert "LocalizedValue" in repr_str
        assert "en" in repr_str

    def test_init_with_expression(self) -> None:
        """Test that expressions are not converted to string."""
        value = LocalizedValue({"en": F("other")})
        assert isinstance(value.en, F)

    def test_callable_value(self) -> None:
        """Test initialization with callable."""
        value = LocalizedValue(lambda: {"en": "from callable"})
        assert value.get("en") == "from callable"


class TestLocalizedStringValue:
    """Tests for LocalizedStringValue."""

    def test_default_value_is_empty_string(self) -> None:
        """Test that default value is empty string."""
        value = LocalizedStringValue()
        for lang_code, _ in settings.LANGUAGES:
            assert value.get(lang_code) == ""

    def test_is_empty_with_empty_strings(self) -> None:
        """Test is_empty() returns True with empty strings."""
        value = LocalizedStringValue()
        assert value.is_empty()


class TestLocalizedBooleanValue:
    """Tests for LocalizedBooleanValue."""

    def test_default_value_is_none(self) -> None:
        """Test that default value is None."""
        value = LocalizedBooleanValue()
        for lang_code, _ in settings.LANGUAGES:
            assert value.get(lang_code) is None

    def test_translate_boolean(self) -> None:
        """Test translate returns boolean."""
        value = LocalizedBooleanValue({"en": True})
        with translation.override("en"):
            assert value.translate() is True

    def test_translate_string_to_boolean(self) -> None:
        """Test translate converts string to boolean."""
        value = LocalizedBooleanValue({"en": "true"})
        with translation.override("en"):
            assert value.translate() is True

        value = LocalizedBooleanValue({"en": "false"})
        with translation.override("en"):
            assert value.translate() is False

    def test_translate_empty_string(self) -> None:
        """Test translate returns None for empty string."""
        value = LocalizedBooleanValue({"en": ""})
        with translation.override("en"):
            assert value.translate() is None

    def test_bool_conversion(self) -> None:
        """Test __bool__ method."""
        value = LocalizedBooleanValue({"en": True})
        with translation.override("en"):
            assert bool(value) is True

        value = LocalizedBooleanValue({"en": False})
        with translation.override("en"):
            assert bool(value) is False

        value = LocalizedBooleanValue()
        with translation.override("en"):
            assert bool(value) is False

    def test_str_representation(self) -> None:
        """Test __str__ method."""
        value = LocalizedBooleanValue({"en": True})
        with translation.override("en"):
            assert str(value) == "True"

        value = LocalizedBooleanValue()
        with translation.override("en"):
            assert str(value) == ""


class TestLocalizedNumericValue:
    """Tests for LocalizedNumericValue base class."""

    def test_int_conversion(self) -> None:
        """Test __int__ method."""
        value = LocalizedNumericValue({"en": 42})
        with translation.override("en"):
            assert int(value) == 42

        value = LocalizedNumericValue()
        with translation.override("en"):
            assert int(value) == 0

    def test_float_conversion(self) -> None:
        """Test __float__ method."""
        value = LocalizedNumericValue({"en": 3.14})
        with translation.override("en"):
            assert float(value) == 3.14

        value = LocalizedNumericValue()
        with translation.override("en"):
            assert float(value) == 0.0


class TestLocalizedIntegerValue:
    """Tests for LocalizedIntegerValue."""

    def test_default_value_is_none(self) -> None:
        """Test that default value is None."""
        value = LocalizedIntegerValue()
        for lang_code, _ in settings.LANGUAGES:
            assert value.get(lang_code) is None

    def test_translate_integer(self) -> None:
        """Test translate returns integer."""
        value = LocalizedIntegerValue({"en": 42})
        with translation.override("en"):
            assert value.translate() == 42
            assert isinstance(value.translate(), int)

    def test_translate_string_to_integer(self) -> None:
        """Test translate converts string to integer."""
        value = LocalizedIntegerValue({"en": "123"})
        with translation.override("en"):
            assert value.translate() == 123

    def test_translate_empty_string(self) -> None:
        """Test translate returns None for empty string."""
        value = LocalizedIntegerValue({"en": ""})
        with translation.override("en"):
            assert value.translate() is None

    def test_translate_invalid_string(self) -> None:
        """Test translate returns None for invalid string."""
        value = LocalizedIntegerValue({"en": "not a number"})
        with translation.override("en"):
            assert value.translate() is None


class TestLocalizedFloatValue:
    """Tests for LocalizedFloatValue."""

    def test_default_value_is_none(self) -> None:
        """Test that default value is None."""
        value = LocalizedFloatValue()
        for lang_code, _ in settings.LANGUAGES:
            assert value.get(lang_code) is None

    def test_translate_float(self) -> None:
        """Test translate returns float."""
        value = LocalizedFloatValue({"en": 3.14})
        with translation.override("en"):
            assert value.translate() == 3.14
            assert isinstance(value.translate(), float)

    def test_translate_int_to_float(self) -> None:
        """Test translate converts int to float."""
        value = LocalizedFloatValue({"en": 42})
        with translation.override("en"):
            result = value.translate()
            assert result == 42.0
            assert isinstance(result, float)

    def test_translate_string_to_float(self) -> None:
        """Test translate converts string to float."""
        value = LocalizedFloatValue({"en": "3.14"})
        with translation.override("en"):
            assert value.translate() == 3.14

    def test_translate_empty_string(self) -> None:
        """Test translate returns None for empty string."""
        value = LocalizedFloatValue({"en": ""})
        with translation.override("en"):
            assert value.translate() is None

    def test_translate_invalid_string(self) -> None:
        """Test translate returns None for invalid string."""
        value = LocalizedFloatValue({"en": "not a number"})
        with translation.override("en"):
            assert value.translate() is None


class TestLocalizedFileValue:
    """Tests for LocalizedFileValue."""

    def test_default_value_is_none(self) -> None:
        """Test that default value is None."""
        value = LocalizedFileValue()
        for lang_code, _ in settings.LANGUAGES:
            assert value.get(lang_code) is None

    def test_str_representation(self) -> None:
        """Test __str__ method."""
        value = LocalizedFileValue({"en": "path/to/file.txt"})
        with translation.override("en"):
            assert str(value) == "path/to/file.txt"

    def test_getattr_proxy(self) -> None:
        """Test __getattr__ proxies to current language file."""

        class MockFile:
            name = "test.txt"
            url = "/media/test.txt"

        value = LocalizedFileValue({"en": MockFile()})
        with translation.override("en"):
            assert value.name == "test.txt"
            assert value.url == "/media/test.txt"

    def test_getattr_raises_for_missing(self) -> None:
        """Test __getattr__ raises AttributeError for missing attributes."""
        value = LocalizedFileValue({"en": "simple_string"})
        with translation.override("en"):
            with pytest.raises(AttributeError):
                _ = value.nonexistent_attr
