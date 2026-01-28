"""Tests for form fields and widgets."""

from django import forms
from django.conf import settings

import pytest
from i18n_fields.forms import (
    LocalizedBooleanFieldForm,
    LocalizedCharFieldForm,
    LocalizedFieldForm,
    LocalizedFileFieldForm,
    LocalizedFloatFieldForm,
    LocalizedIntegerFieldForm,
    LocalizedTextFieldForm,
)
from i18n_fields.value import (
    LocalizedBooleanValue,
    LocalizedFloatValue,
    LocalizedIntegerValue,
    LocalizedStringValue,
    LocalizedValue,
)
from i18n_fields.widgets import (
    AdminLocalizedBooleanFieldWidget,
    AdminLocalizedCharFieldWidget,
    AdminLocalizedFieldWidget,
    AdminLocalizedFileFieldWidget,
    AdminLocalizedFloatFieldWidget,
    AdminLocalizedIntegerFieldWidget,
    LocalizedCharFieldWidget,
    LocalizedFieldWidget,
    LocalizedFileWidget,
)


class TestLocalizedFieldForm:
    """Tests for LocalizedFieldForm."""

    def test_init_creates_fields_for_languages(self) -> None:
        """Test form creates field for each language."""
        form_field = LocalizedFieldForm()

        assert len(form_field.fields) == len(settings.LANGUAGES)

    def test_init_sets_language_labels(self) -> None:
        """Test form fields have language labels."""
        form_field = LocalizedFieldForm()

        labels = [f.label for f in form_field.fields]
        lang_codes = [code for code, _ in settings.LANGUAGES]
        assert labels == lang_codes

    def test_required_false_means_no_fields_required(self) -> None:
        """Test required=False makes all fields optional."""
        form_field = LocalizedFieldForm(required=False)

        assert not form_field.required
        for field in form_field.fields:
            assert not field.required

    def test_required_true_means_form_required(self) -> None:
        """Test required=True makes form required."""
        form_field = LocalizedFieldForm(required=True)

        assert form_field.required

    def test_required_list_marks_specific_fields(self) -> None:
        """Test required list marks specific language fields."""
        required_langs = ["en", "nl"]
        form_field = LocalizedFieldForm(required=required_langs)

        assert form_field.required  # Form is required
        for field in form_field.fields:
            if field.label in required_langs:
                assert field.required
            else:
                assert not field.required

    def test_compress_returns_localized_value(self) -> None:
        """Test compress returns LocalizedValue."""
        form_field = LocalizedFieldForm()
        values = ["English", "Dutch", "Romanian", "German"]

        result = form_field.compress(values)

        assert isinstance(result, LocalizedValue)
        for (lang_code, _), value in zip(settings.LANGUAGES, values, strict=False):
            assert result.get(lang_code) == value

    def test_value_class(self) -> None:
        """Test form uses correct value class."""
        assert LocalizedFieldForm.value_class == LocalizedValue

    def test_field_class(self) -> None:
        """Test form uses correct field class."""
        assert LocalizedFieldForm.field_class == forms.fields.CharField


class TestLocalizedCharFieldForm:
    """Tests for LocalizedCharFieldForm."""

    def test_value_class(self) -> None:
        """Test uses LocalizedStringValue."""
        assert LocalizedCharFieldForm.value_class == LocalizedStringValue

    def test_widget(self) -> None:
        """Test uses LocalizedCharFieldWidget."""
        assert LocalizedCharFieldForm.widget == LocalizedCharFieldWidget


class TestLocalizedTextFieldForm:
    """Tests for LocalizedTextFieldForm."""

    def test_value_class(self) -> None:
        """Test uses LocalizedStringValue."""
        assert LocalizedTextFieldForm.value_class == LocalizedStringValue


class TestLocalizedIntegerFieldForm:
    """Tests for LocalizedIntegerFieldForm."""

    def test_value_class(self) -> None:
        """Test uses LocalizedIntegerValue."""
        assert LocalizedIntegerFieldForm.value_class == LocalizedIntegerValue

    def test_field_class(self) -> None:
        """Test uses IntegerField."""
        assert LocalizedIntegerFieldForm.field_class == forms.fields.IntegerField


class TestLocalizedFloatFieldForm:
    """Tests for LocalizedFloatFieldForm."""

    def test_value_class(self) -> None:
        """Test uses LocalizedFloatValue."""
        assert LocalizedFloatFieldForm.value_class == LocalizedFloatValue

    def test_field_class(self) -> None:
        """Test uses FloatField."""
        assert LocalizedFloatFieldForm.field_class == forms.fields.FloatField


class TestLocalizedBooleanFieldForm:
    """Tests for LocalizedBooleanFieldForm."""

    def test_value_class(self) -> None:
        """Test uses LocalizedBooleanValue."""
        assert LocalizedBooleanFieldForm.value_class == LocalizedBooleanValue

    def test_field_class(self) -> None:
        """Test uses NullBooleanField."""
        assert LocalizedBooleanFieldForm.field_class == forms.fields.NullBooleanField


class TestLocalizedFileFieldForm:
    """Tests for LocalizedFileFieldForm."""

    def test_widget(self) -> None:
        """Test uses LocalizedFileWidget."""
        assert LocalizedFileFieldForm.widget == LocalizedFileWidget

    def test_field_class(self) -> None:
        """Test uses FileField."""
        assert LocalizedFileFieldForm.field_class == forms.fields.FileField

    def test_clean_with_empty_values_required_true(self) -> None:
        """Test clean raises ValidationError when required and values are empty."""

        from django.core.exceptions import ValidationError

        form_field = LocalizedFileFieldForm(required=True)
        empty_values = [None for _ in settings.LANGUAGES]

        with pytest.raises(ValidationError) as exc_info:
            form_field.clean(empty_values)

        assert exc_info.value.code == "required"

    def test_clean_with_empty_values_required_false(self) -> None:
        """Test clean succeeds when not required and values are empty."""
        from i18n_fields.value import LocalizedFileValue

        form_field = LocalizedFileFieldForm(required=False)
        empty_values = [None for _ in settings.LANGUAGES]

        result = form_field.clean(empty_values)

        assert isinstance(result, LocalizedFileValue)

    def test_clean_with_invalid_non_list_value(self) -> None:
        """Test clean raises ValidationError for non-list value."""
        from django.core.exceptions import ValidationError

        form_field = LocalizedFileFieldForm()

        with pytest.raises(ValidationError) as exc_info:
            form_field.clean("not a list")

        assert exc_info.value.code == "invalid"

    def test_clean_with_initial_none(self) -> None:
        """Test clean handles initial=None by creating list of None."""
        from unittest.mock import Mock

        from i18n_fields.value import LocalizedFileValue

        form_field = LocalizedFileFieldForm(required=False)

        # Create mock file objects
        mock_files = [Mock() for _ in settings.LANGUAGES]
        for mock_file in mock_files:
            mock_file.name = "test.txt"
            mock_file.size = 100

        result = form_field.clean(mock_files, initial=None)

        assert isinstance(result, LocalizedFileValue)

    def test_clean_with_initial_non_list(self) -> None:
        """Test clean decompresses initial when not a list."""
        from unittest.mock import Mock

        from i18n_fields.value import LocalizedFileValue

        form_field = LocalizedFileFieldForm(required=False)

        # Create mock file objects
        mock_files = [Mock() for _ in settings.LANGUAGES]
        for mock_file in mock_files:
            mock_file.name = "test.txt"
            mock_file.size = 100

        # Create mock initial value
        initial_value = LocalizedFileValue({"en": Mock(name="old.txt")})

        result = form_field.clean(mock_files, initial=initial_value)

        assert isinstance(result, LocalizedFileValue)

    def test_clean_with_field_validation_error(self) -> None:
        """Test clean collects ValidationErrors from individual fields."""
        from unittest.mock import Mock, patch

        from django.core.exceptions import ValidationError

        form_field = LocalizedFileFieldForm(required=False)

        # Create values that will cause field validation errors
        # File fields raise ValidationError for invalid file types, sizes, etc.
        values = [Mock() for _ in settings.LANGUAGES]

        # Patch one of the fields to raise ValidationError
        with patch.object(form_field.fields[0], "clean") as mock_clean:
            mock_clean.side_effect = ValidationError("Invalid file", code="invalid")

            with pytest.raises(ValidationError):
                form_field.clean(values)

    def test_clean_with_require_all_fields_and_missing_required(self) -> None:
        """Test clean with require_all_fields=True and missing values."""
        from django.core.exceptions import ValidationError

        form_field = LocalizedFileFieldForm(required=True)
        form_field.require_all_fields = True

        # Empty values with require_all_fields should raise
        empty_values = [None for _ in settings.LANGUAGES]

        with pytest.raises(ValidationError):
            form_field.clean(empty_values)

    def test_clean_with_specific_field_required(self) -> None:
        """Test clean when specific language field is required."""
        from unittest.mock import Mock

        from django.core.exceptions import ValidationError

        # Make only "en" required
        form_field = LocalizedFileFieldForm(required=["en"])

        # Provide values for all languages except "en"
        values = []
        for lang_code, _ in settings.LANGUAGES:
            if lang_code == "en":
                values.append(None)  # Missing required "en"
            else:
                values.append(Mock(name="test.txt", size=100))

        with pytest.raises(ValidationError):
            form_field.clean(values)

    def test_bound_data_with_none_initial(self) -> None:
        """Test bound_data creates list of None when initial is None."""
        from unittest.mock import Mock

        form_field = LocalizedFileFieldForm()
        data = [Mock(name="test.txt") for _ in settings.LANGUAGES]

        result = form_field.bound_data(data, initial=None)

        assert isinstance(result, list)
        assert len(result) == len(data)
        assert result == data  # Should return data when initial is None

    def test_bound_data_with_non_list_initial(self) -> None:
        """Test bound_data decompresses initial when not a list."""
        from unittest.mock import Mock

        from i18n_fields.value import LocalizedFileValue

        form_field = LocalizedFileFieldForm()
        data = [Mock(name="new.txt") for _ in settings.LANGUAGES]
        initial_value = LocalizedFileValue({"en": Mock(name="old.txt")})

        result = form_field.bound_data(data, initial_value)

        assert isinstance(result, list)
        assert len(result) == len(data)

    def test_bound_data_with_file_input_contradiction(self) -> None:
        """Test bound_data handles FILE_INPUT_CONTRADICTION."""
        from unittest.mock import Mock

        from django.forms.widgets import FILE_INPUT_CONTRADICTION

        form_field = LocalizedFileFieldForm()
        initial_files = [Mock(name=f"old_{i}.txt") for i in range(len(settings.LANGUAGES))]

        # Create data with FILE_INPUT_CONTRADICTION
        data = []
        for i in range(len(settings.LANGUAGES)):
            if i == 0:
                data.append(FILE_INPUT_CONTRADICTION)
            else:
                data.append(None)

        result = form_field.bound_data(data, initial_files)

        # FILE_INPUT_CONTRADICTION and None should use initial values
        assert result[0] == initial_files[0]
        assert result[1] == initial_files[1]

    def test_bound_data_with_none_in_data(self) -> None:
        """Test bound_data returns initial value when data is None."""
        from unittest.mock import Mock

        form_field = LocalizedFileFieldForm()
        initial_files = [Mock(name=f"old_{i}.txt") for i in range(len(settings.LANGUAGES))]
        data = [None for _ in settings.LANGUAGES]

        result = form_field.bound_data(data, initial_files)

        # None in data should use initial values
        assert result == initial_files


class TestLocalizedFieldWidget:
    """Tests for LocalizedFieldWidget."""

    def test_creates_widgets_for_languages(self) -> None:
        """Test widget creates sub-widget for each language."""
        widget = LocalizedFieldWidget()

        assert len(widget.widgets) == len(settings.LANGUAGES)

    def test_widgets_have_lang_attributes(self) -> None:
        """Test sub-widgets have language attributes."""
        widget = LocalizedFieldWidget()

        for (lang_code, lang_name), sub_widget in zip(
            settings.LANGUAGES, widget.widgets, strict=False
        ):
            assert sub_widget.lang_code == lang_code
            assert sub_widget.lang_name == lang_name
            assert sub_widget.attrs.get("lang") == lang_code

    def test_decompress_dict(self) -> None:
        """Test decompress with dictionary."""
        widget = LocalizedFieldWidget()
        value = {"en": "English", "nl": "Dutch"}

        result = widget.decompress(value)

        assert isinstance(result, list)
        assert len(result) == len(settings.LANGUAGES)

    def test_decompress_localized_value(self) -> None:
        """Test decompress with LocalizedValue."""
        widget = LocalizedFieldWidget()
        value = LocalizedValue({"en": "English", "nl": "Dutch"})

        result = widget.decompress(value)

        assert isinstance(result, list)
        assert result[0] == "English"  # Assuming en is first

    def test_decompress_none(self) -> None:
        """Test decompress with None."""
        widget = LocalizedFieldWidget()

        result = widget.decompress(None)

        assert isinstance(result, list)
        assert len(result) == len(settings.LANGUAGES)
        assert all(v is None for v in result)

    def test_decompress_string(self) -> None:
        """Test decompress with string."""
        widget = LocalizedFieldWidget()

        result = widget.decompress("simple string")

        # Should set primary language value
        assert isinstance(result, list)

    def test_decompress_fallback_for_unknown_type(self) -> None:
        """Test decompress fallback for unknown types."""
        widget = LocalizedFieldWidget()

        # Use an object that's not None, str, or dict
        result = widget.decompress(123)  # type: ignore[arg-type]

        # Should return list of Nones as fallback
        assert isinstance(result, list)
        assert len(result) == len(settings.LANGUAGES)
        assert all(v is None for v in result)

    def test_get_context_basic(self) -> None:
        """Test get_context returns proper context."""
        widget = LocalizedFieldWidget()
        context = widget.get_context("test_field", None, {})

        assert "widget" in context
        assert "subwidgets" in context["widget"]
        assert len(context["widget"]["subwidgets"]) == len(settings.LANGUAGES)

    def test_get_context_with_value(self) -> None:
        """Test get_context with a value."""
        widget = LocalizedFieldWidget()
        value = LocalizedValue({"en": "Test", "nl": "Test NL"})
        context = widget.get_context("test_field", value, {})

        assert "subwidgets" in context["widget"]
        subwidgets = context["widget"]["subwidgets"]
        assert len(subwidgets) == len(settings.LANGUAGES)

        # Check that subwidgets have lang_code and lang_name
        for subwidget in subwidgets:
            assert "lang_code" in subwidget
            assert "lang_name" in subwidget

    def test_get_context_with_id_attrs(self) -> None:
        """Test get_context with id in attrs."""
        widget = LocalizedFieldWidget()
        context = widget.get_context("test_field", None, {"id": "my_field"})

        subwidgets = context["widget"]["subwidgets"]
        # Each subwidget should have unique ID with language code
        for subwidget, (lang_code, _) in zip(subwidgets, settings.LANGUAGES, strict=False):
            assert subwidget["attrs"]["id"] == f"my_field_{lang_code}"

    def test_get_context_with_list_value(self) -> None:
        """Test get_context with list value."""
        widget = LocalizedFieldWidget()
        values = ["Value 1", "Value 2", "Value 3", "Value 4"]
        context = widget.get_context("test_field", values, {})

        assert "subwidgets" in context["widget"]
        assert len(context["widget"]["subwidgets"]) == len(settings.LANGUAGES)

    def test_get_context_with_input_type(self) -> None:
        """Test get_context preserves input_type."""
        widget = LocalizedFieldWidget()
        context = widget.get_context("test_field", None, {"type": "text"})

        # Input type should be passed to subwidgets
        assert "subwidgets" in context["widget"]

    def test_get_context_with_is_localized(self) -> None:
        """Test get_context propagates is_localized to subwidgets."""
        widget = LocalizedFieldWidget()
        widget.is_localized = True
        widget.get_context("test_field", None, {})

        # All subwidgets should have is_localized=True
        for subwidget_obj in widget.widgets:
            assert subwidget_obj.is_localized is True

    def test_build_widget_attrs_removes_required_when_not_needed(self) -> None:
        """Test build_widget_attrs removes 'required' when not needed."""
        from unittest.mock import Mock

        widget_mock = Mock()
        widget_mock.use_required_attribute.return_value = False
        widget_mock.is_required = False

        attrs = {"required": True, "class": "test"}
        result = LocalizedFieldWidget.build_widget_attrs(widget_mock, None, attrs)

        assert "required" not in result
        assert result["class"] == "test"

    def test_build_widget_attrs_keeps_required_when_needed(self) -> None:
        """Test build_widget_attrs keeps 'required' when needed."""
        from unittest.mock import Mock

        widget_mock = Mock()
        widget_mock.use_required_attribute.return_value = True
        widget_mock.is_required = True

        attrs = {"required": True, "class": "test"}
        result = LocalizedFieldWidget.build_widget_attrs(widget_mock, None, attrs)

        assert result["required"] is True
        assert result["class"] == "test"

    def test_template_name(self) -> None:
        """Test widget uses correct template."""
        widget = LocalizedFieldWidget()
        assert widget.template_name == "i18n_fields/multiwidget.html"


class TestLocalizedCharFieldWidget:
    """Tests for LocalizedCharFieldWidget."""

    def test_widget_is_text_input(self) -> None:
        """Test uses TextInput as sub-widget."""
        assert LocalizedCharFieldWidget.widget == forms.TextInput


class TestLocalizedFileWidget:
    """Tests for LocalizedFileWidget."""

    def test_widget_is_clearable_file_input(self) -> None:
        """Test uses ClearableFileInput as sub-widget."""
        assert LocalizedFileWidget.widget == forms.ClearableFileInput


class TestAdminLocalizedFieldWidget:
    """Tests for AdminLocalizedFieldWidget."""

    def test_default_display_mode_from_settings(self) -> None:
        """Test display mode defaults to settings value."""
        widget = AdminLocalizedFieldWidget()
        # Default from settings is "tab"
        assert widget.display_mode == "tab"

    def test_custom_display_mode(self) -> None:
        """Test custom display mode."""
        widget = AdminLocalizedFieldWidget(display_mode="dropdown")
        assert widget.display_mode == "dropdown"

    def test_template_name_tab_mode(self) -> None:
        """Test template for tab mode."""
        widget = AdminLocalizedFieldWidget(display_mode="tab")
        assert "widget_tabs.html" in widget.template_name

    def test_template_name_dropdown_mode(self) -> None:
        """Test template for dropdown mode."""
        widget = AdminLocalizedFieldWidget(display_mode="dropdown")
        assert "widget_dropdown.html" in widget.template_name


class TestAdminWidgetSubclasses:
    """Tests for admin widget subclasses."""

    def test_admin_char_field_widget(self) -> None:
        """Test AdminLocalizedCharFieldWidget."""
        from django.contrib.admin import widgets

        assert AdminLocalizedCharFieldWidget.widget == widgets.AdminTextInputWidget

    def test_admin_file_field_widget(self) -> None:
        """Test AdminLocalizedFileFieldWidget."""
        from django.contrib.admin import widgets

        assert AdminLocalizedFileFieldWidget.widget == widgets.AdminFileWidget

    def test_admin_boolean_field_widget(self) -> None:
        """Test AdminLocalizedBooleanFieldWidget."""
        assert AdminLocalizedBooleanFieldWidget.widget == forms.NullBooleanSelect

    def test_admin_boolean_field_widget_init(self) -> None:
        """Test AdminLocalizedBooleanFieldWidget initialization."""
        widget = AdminLocalizedBooleanFieldWidget(display_mode="dropdown")
        assert widget.display_mode == "dropdown"
        assert len(widget.widgets) == len(settings.LANGUAGES)

    def test_admin_integer_field_widget(self) -> None:
        """Test AdminLocalizedIntegerFieldWidget."""
        from django.contrib.admin import widgets

        assert AdminLocalizedIntegerFieldWidget.widget == widgets.AdminIntegerFieldWidget

    def test_admin_float_field_widget(self) -> None:
        """Test AdminLocalizedFloatFieldWidget."""
        assert AdminLocalizedFloatFieldWidget.widget == forms.NumberInput
