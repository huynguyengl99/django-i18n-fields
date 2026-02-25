"""Tests for the md (martor) module."""

from unittest import mock

from django.conf import settings

import pytest
from i18n_fields.md.fields import LocalizedMartorField
from i18n_fields.md.forms import LocalizedMartorForm
from i18n_fields.md.widgets import (
    AdminLocalizedMartorWidget,
    LocalizedMartorWidget,
)
from i18n_fields.value import LocalizedStringValue
from i18n_fields.widgets import AdminLocalizedFieldWidget, LocalizedFieldWidget

from .fake_model import cleanup_fake_model, get_fake_model


class TestLocalizedMartorWidget:
    """Tests for LocalizedMartorWidget."""

    def test_inherits_from_localized_field_widget(self) -> None:
        assert issubclass(LocalizedMartorWidget, LocalizedFieldWidget)

    def test_creates_widgets_for_each_language(self) -> None:
        widget = LocalizedMartorWidget()
        assert len(widget.widgets) == len(settings.LANGUAGES)


class TestAdminLocalizedMartorWidget:
    """Tests for AdminLocalizedMartorWidget."""

    def test_inherits_from_admin_localized_field_widget(self) -> None:
        assert issubclass(AdminLocalizedMartorWidget, AdminLocalizedFieldWidget)

    def test_creates_widgets_for_each_language(self) -> None:
        widget = AdminLocalizedMartorWidget()
        assert len(widget.widgets) == len(settings.LANGUAGES)

    @mock.patch("i18n_fields.md.widgets.reverse", return_value="/martor/markdownfy/")
    @mock.patch(
        "i18n_fields.md.widgets.get_template",
        return_value=mock.MagicMock(render=mock.MagicMock(return_value="")),
    )
    def test_markdown_render_escapes_field_name(self, _mock_tpl, _mock_rev) -> None:
        """Test that markdown_render escapes field_name via format_html."""
        widget = AdminLocalizedMartorWidget()
        result = widget.markdown_render(
            name='test<script>alert("xss")</script>',
            value="",
            attrs={"id": "test-id"},
        )
        html = str(result)
        # The field_name (which includes the name) should be escaped
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert 'class="main-martor"' in html

    @mock.patch("i18n_fields.md.widgets.reverse", return_value="/martor/markdownfy/")
    @mock.patch(
        "i18n_fields.md.widgets.get_template",
        return_value=mock.MagicMock(render=mock.MagicMock(return_value="")),
    )
    def test_markdown_render_id_uses_random_string(self, _mock_tpl, _mock_rev) -> None:
        """Test that rendered IDs use cryptographic random strings."""
        widget = AdminLocalizedMartorWidget()
        result1 = widget.markdown_render(
            name="field", value="", attrs={"id": "my-id"}
        )
        result2 = widget.markdown_render(
            name="field", value="", attrs={"id": "my-id"}
        )
        # Two renders should produce different IDs (random suffix)
        assert str(result1) != str(result2)

    @mock.patch("i18n_fields.md.widgets.reverse", return_value="/martor/markdownfy/")
    @mock.patch(
        "i18n_fields.md.widgets.get_template",
        return_value=mock.MagicMock(render=mock.MagicMock(return_value="")),
    )
    def test_markdown_render_returns_safe_string(self, _mock_tpl, _mock_rev) -> None:
        """Test that result is a SafeString (from format_html)."""
        from django.utils.safestring import SafeString

        widget = AdminLocalizedMartorWidget()
        result = widget.markdown_render(
            name="field", value="", attrs={"id": "my-id"}
        )
        assert isinstance(result, SafeString)


class TestLocalizedMartorForm:
    """Tests for LocalizedMartorForm."""

    def test_uses_localized_martor_widget(self) -> None:
        assert LocalizedMartorForm.widget is LocalizedMartorWidget

    def test_uses_localized_string_value(self) -> None:
        assert LocalizedMartorForm.value_class is LocalizedStringValue

    def test_creates_fields_for_each_language(self) -> None:
        form = LocalizedMartorForm()
        assert len(form.fields) == len(settings.LANGUAGES)

    def test_compress_returns_localized_string_value(self) -> None:
        form = LocalizedMartorForm()
        data = ["hello"] + [""] * (len(settings.LANGUAGES) - 1)
        result = form.compress(data)
        assert isinstance(result, LocalizedStringValue)
        assert result.get("en") == "hello"


class TestLocalizedMartorField:
    """Tests for LocalizedMartorField model field."""

    def test_attr_class_is_localized_string_value(self) -> None:
        field = LocalizedMartorField()
        assert field.attr_class is LocalizedStringValue

    def test_formfield_returns_martor_form(self) -> None:
        field = LocalizedMartorField()
        form_field = field.formfield()
        assert isinstance(form_field, LocalizedMartorForm)

    def test_formfield_uses_admin_martor_widget(self) -> None:
        field = LocalizedMartorField()
        form_field = field.formfield()
        assert isinstance(form_field.widget, AdminLocalizedMartorWidget)

    def test_formfield_passes_display_mode(self) -> None:
        field = LocalizedMartorField()
        mock_widget = mock.MagicMock()
        mock_widget.display_mode = "dropdown"
        form_field = field.formfield(widget=mock_widget)
        assert isinstance(form_field.widget, AdminLocalizedMartorWidget)
        assert form_field.widget.display_mode == "dropdown"

    @pytest.fixture()
    def martor_model(self):
        model = get_fake_model(
            {"content": LocalizedMartorField(blank=True, default=dict)}
        )
        yield model
        cleanup_fake_model(model)

    @pytest.mark.django_db
    def test_create_and_read(self, martor_model) -> None:
        """Test that LocalizedMartorField can store and retrieve values."""
        obj = martor_model.objects.create(content={"en": "# Hello", "nl": "# Hallo"})
        obj.refresh_from_db()
        assert obj.content.get("en") == "# Hello"
        assert obj.content.get("nl") == "# Hallo"

    @pytest.mark.django_db
    def test_default_is_empty(self, martor_model) -> None:
        obj = martor_model.objects.create()
        obj.refresh_from_db()
        assert obj.content.get("en") == ""





