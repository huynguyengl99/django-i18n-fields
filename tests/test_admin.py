"""Tests for admin integration."""

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

import pytest
from i18n_fields.admin import (
    FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS,
    LocalizedFieldsAdminMixin,
    _get_localized_field_display,
    _get_localized_field_readonly_display,
)
from i18n_fields.fields import (
    LocalizedBooleanField,
    LocalizedCharField,
    LocalizedField,
    LocalizedFileField,
    LocalizedFloatField,
    LocalizedIntegerField,
    LocalizedTextField,
)
from i18n_fields.value import LocalizedValue
from i18n_fields.widgets import (
    AdminLocalizedBooleanFieldWidget,
    AdminLocalizedCharFieldWidget,
    AdminLocalizedFieldWidget,
    AdminLocalizedFileFieldWidget,
    AdminLocalizedFloatFieldWidget,
    AdminLocalizedIntegerFieldWidget,
)

from .fake_model import cleanup_fake_model, get_fake_model


class TestFormfieldForLocalizedFieldsDefaults:
    """Tests for the formfield mapping defaults."""

    def test_mapping_contains_all_field_types(self) -> None:
        """Test all field types are mapped."""
        assert LocalizedField in FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS
        assert LocalizedCharField in FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS
        assert LocalizedTextField in FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS
        assert LocalizedIntegerField in FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS
        assert LocalizedFloatField in FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS
        assert LocalizedBooleanField in FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS
        assert LocalizedFileField in FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS

    def test_mapping_uses_correct_widgets(self) -> None:
        """Test field types map to correct widgets."""
        assert (
            FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS[LocalizedCharField]
            == AdminLocalizedCharFieldWidget
        )
        assert (
            FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS[LocalizedTextField]
            == AdminLocalizedFieldWidget
        )
        assert (
            FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS[LocalizedIntegerField]
            == AdminLocalizedIntegerFieldWidget
        )
        assert (
            FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS[LocalizedFloatField]
            == AdminLocalizedFloatFieldWidget
        )
        assert (
            FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS[LocalizedBooleanField]
            == AdminLocalizedBooleanFieldWidget
        )
        assert (
            FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS[LocalizedFileField]
            == AdminLocalizedFileFieldWidget
        )


class TestGetLocalizedFieldDisplay:
    """Tests for _get_localized_field_display helper."""

    def test_returns_translated_value(self) -> None:
        """Test returns translated value."""

        class MockObj:
            title = LocalizedValue({"en": "Test Title"})

        result = _get_localized_field_display(MockObj(), "title")
        assert result == "Test Title"

    def test_returns_dash_for_none(self) -> None:
        """Test returns dash for None value."""

        class MockObj:
            title = None

        result = _get_localized_field_display(MockObj(), "title")
        assert result == "-"

    def test_returns_dash_for_empty(self) -> None:
        """Test returns dash for empty value."""

        class MockObj:
            title = LocalizedValue()

        result = _get_localized_field_display(MockObj(), "title")
        assert result == "-"

    def test_handles_dict_value(self) -> None:
        """Test handles raw dict value."""

        class MockObj:
            title = {"en": "Dict Value"}

        result = _get_localized_field_display(MockObj(), "title")
        assert result == "Dict Value"


class TestGetLocalizedFieldReadonlyDisplay:
    """Tests for _get_localized_field_readonly_display helper."""

    def test_returns_html_for_tab_mode(self) -> None:
        """Test returns tab HTML."""

        class MockObj:
            title = LocalizedValue({"en": "English", "nl": "Dutch"})

        result = _get_localized_field_readonly_display(MockObj(), "title", "tab")
        assert "i18n-readonly-widget" in result
        assert "i18n-tab-mode" in result
        assert "i18n-readonly-tab" in result
        assert "English" in result

    def test_returns_html_for_dropdown_mode(self) -> None:
        """Test returns dropdown HTML."""

        class MockObj:
            title = LocalizedValue({"en": "English", "nl": "Dutch"})

        result = _get_localized_field_readonly_display(MockObj(), "title", "dropdown")
        assert "i18n-readonly-widget" in result
        assert "i18n-dropdown-mode" in result
        assert "i18n-readonly-select" in result

    def test_handles_none_value(self) -> None:
        """Test handles None value."""

        class MockObj:
            title = None

        result = _get_localized_field_readonly_display(MockObj(), "title")
        assert "i18n-readonly-widget" in result

    def test_handles_dict_value(self) -> None:
        """Test handles raw dict value."""

        class MockObj:
            title = {"en": "Raw Dict"}

        result = _get_localized_field_readonly_display(MockObj(), "title")
        assert "Raw Dict" in result


@pytest.mark.django_db(transaction=True)
class TestLocalizedFieldsAdminMixin:
    """Tests for LocalizedFieldsAdminMixin."""

    @pytest.fixture
    def article_model(self):
        """Create article model with localized fields."""
        model = get_fake_model({
            "title": LocalizedCharField(),
            "content": LocalizedTextField(blank=True),
            "rating": LocalizedFloatField(blank=True, null=True),
        })
        yield model
        cleanup_fake_model(model)

    @pytest.fixture
    def admin_class(self, article_model):
        """Create admin class with mixin."""

        class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
            list_display = ["id", "title"]

        return ArticleAdmin

    @pytest.fixture
    def admin_site(self):
        """Create admin site."""
        return AdminSite()

    @pytest.fixture
    def request_factory(self):
        """Create request factory."""
        return RequestFactory()

    def test_mixin_has_media(self, admin_class, article_model, admin_site) -> None:
        """Test mixin adds media files."""
        admin_instance = admin_class(article_model, admin_site)

        media = admin_instance.media
        # Check CSS
        assert any("i18n-fields-admin.css" in str(css) for css in media._css.get("all", []))
        # Check JS
        assert any("i18n-fields-admin.js" in str(js) for js in media._js)

    def test_formfield_for_dbfield_uses_widget(
        self, admin_class, article_model, admin_site, request_factory
    ) -> None:
        """Test formfield_for_dbfield uses correct widget."""
        admin_instance = admin_class(article_model, admin_site)
        request = request_factory.get("/admin/")

        title_field = article_model._meta.get_field("title")
        form_field = admin_instance.formfield_for_dbfield(title_field, request)

        assert isinstance(form_field.widget, AdminLocalizedCharFieldWidget)

    def test_formfield_respects_display_mode(
        self, article_model, admin_site, request_factory
    ) -> None:
        """Test formfield respects localized_fields_display setting."""

        class DropdownAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
            localized_fields_display = "dropdown"

        admin_instance = DropdownAdmin(article_model, admin_site)
        request = request_factory.get("/admin/")

        title_field = article_model._meta.get_field("title")
        form_field = admin_instance.formfield_for_dbfield(title_field, request)

        assert form_field.widget.display_mode == "dropdown"

    def test_list_display_creates_methods(
        self, admin_class, article_model, admin_site
    ) -> None:
        """Test list_display fields get display methods."""
        admin_instance = admin_class(article_model, admin_site)

        # Should have replaced "title" with a method
        assert "_localized_title_display" in admin_instance.list_display

    def test_readonly_fields_creates_methods(
        self, article_model, admin_site
    ) -> None:
        """Test readonly_fields get display methods."""

        class ReadonlyAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
            readonly_fields = ["title"]

        admin_instance = ReadonlyAdmin(article_model, admin_site)

        # Should have replaced "title" with a method name
        assert "_readonly_title_display" in admin_instance.readonly_fields


@pytest.mark.django_db(transaction=True)
class TestLocalizedFieldsAdminWithModel:
    """Integration tests for admin with actual model operations."""

    @pytest.fixture
    def model_and_admin(self):
        """Create model and admin."""
        model = get_fake_model({
            "title": LocalizedCharField(),
            "active": LocalizedBooleanField(blank=True, null=True),
        })

        class TestAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
            list_display = ["id", "title", "active"]

        admin_instance = TestAdmin(model, AdminSite())

        yield model, admin_instance

        cleanup_fake_model(model)

    def test_admin_display_method_works(self, model_and_admin) -> None:
        """Test display method works with actual object."""
        model, admin_instance = model_and_admin

        obj = model.objects.create(
            title={"en": "Test", "nl": "Test NL"},
            active={"en": True},
        )

        # Get the display method
        method_name = "_localized_title_display"
        if hasattr(admin_instance, method_name):
            display_func = getattr(admin_instance, method_name)
            result = display_func(obj)
            assert result == "Test"
