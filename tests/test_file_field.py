"""Tests for LocalizedFileField."""


from django.conf import settings
from django.core.files.base import ContentFile

import pytest
from i18n_fields.fields import LocalizedFileField
from i18n_fields.fields.file_field import (
    LocalizedFieldFile,
    LocalizedFileValueDescriptor,
)
from i18n_fields.forms import LocalizedFileFieldForm
from i18n_fields.value import LocalizedFileValue

from .fake_model import cleanup_fake_model, get_fake_model


class TestLocalizedFileField:
    """Tests for LocalizedFileField initialization and configuration."""

    def test_attr_class_is_file_value(self) -> None:
        """Test LocalizedFileField uses LocalizedFileValue."""
        field = LocalizedFileField()
        assert field.attr_class == LocalizedFileValue

    def test_descriptor_class(self) -> None:
        """Test LocalizedFileField uses correct descriptor."""
        field = LocalizedFileField()
        assert field.descriptor_class == LocalizedFileValueDescriptor

    def test_value_class(self) -> None:
        """Test LocalizedFileField uses LocalizedFieldFile."""
        field = LocalizedFileField()
        assert field.value_class == LocalizedFieldFile

    def test_upload_to_string(self) -> None:
        """Test upload_to as string."""
        field = LocalizedFileField(upload_to="files/{lang}/")
        assert field.upload_to == "files/{lang}/"

    def test_upload_to_callable(self) -> None:
        """Test upload_to as callable."""

        def custom_upload_to(instance, filename, lang):
            return f"custom/{lang}/{filename}"

        field = LocalizedFileField(upload_to=custom_upload_to)
        assert field.upload_to == custom_upload_to

    def test_formfield_returns_file_form(self) -> None:
        """Test formfield returns LocalizedFileFieldForm."""
        field = LocalizedFileField()
        form_field = field.formfield()
        assert isinstance(form_field, LocalizedFileFieldForm)

    def test_deconstruct_includes_upload_to(self) -> None:
        """Test deconstruct includes upload_to."""
        field = LocalizedFileField(upload_to="files/")
        name, path, args, kwargs = field.deconstruct()

        assert "upload_to" in kwargs
        assert kwargs["upload_to"] == "files/"


class TestLocalizedFileFieldValueConversion:
    """Tests for LocalizedFileField value conversion."""

    def test_get_prep_value_localized_value(self) -> None:
        """Test get_prep_value with LocalizedFileValue."""
        field = LocalizedFileField(blank=True, null=True)

        class MockFile:
            def __str__(self):
                return "path/to/file.txt"

        value = LocalizedFileValue({"en": MockFile(), "nl": None})
        result = field.get_prep_value(value)

        assert isinstance(result, dict)
        assert result["en"] == "path/to/file.txt"

    def test_get_prep_value_none(self) -> None:
        """Test get_prep_value with None."""
        field = LocalizedFileField(blank=True, null=True)
        result = field.get_prep_value(None)
        assert result is None


@pytest.mark.django_db(transaction=True)
class TestLocalizedFileFieldFilenameGeneration:
    """Tests for LocalizedFileField.generate_filename."""

    def test_generate_filename_with_string_upload_to(self) -> None:
        """Test generate_filename with string upload_to."""
        field = LocalizedFileField(upload_to="files/{lang}/")
        # Create a mock model instance
        model = get_fake_model({"document": LocalizedFileField(blank=True, null=True)})
        try:
            instance = model()
            filename = field.generate_filename(instance, "test.txt", "en")
            assert "files/en/" in filename
            assert "test.txt" in filename
        finally:
            cleanup_fake_model(model)

    def test_generate_filename_with_callable(self) -> None:
        """Test generate_filename with callable upload_to."""

        def custom_upload_to(instance, filename, lang):
            return f"custom/{lang}/{filename}"

        field = LocalizedFileField(upload_to=custom_upload_to)
        model = get_fake_model({"document": LocalizedFileField(blank=True, null=True)})
        try:
            instance = model()
            filename = field.generate_filename(instance, "test.txt", "en")
            assert "custom/en/test.txt" in filename
        finally:
            cleanup_fake_model(model)


@pytest.mark.django_db(transaction=True)
class TestLocalizedFileFieldModel:
    """Database tests for LocalizedFileField."""

    def test_create_without_files(self) -> None:
        """Test creating model without files."""
        model = get_fake_model(
            {"document": LocalizedFileField(upload_to="docs/", blank=True, null=True)}
        )
        try:
            obj = model.objects.create()
            # Should have empty file values
            for lang, _ in settings.LANGUAGES:
                assert not obj.document.get(lang)
        finally:
            cleanup_fake_model(model)

    def test_file_value_descriptor(self) -> None:
        """Test file value descriptor wraps files correctly."""
        model = get_fake_model(
            {"document": LocalizedFileField(upload_to="docs/", blank=True, null=True)}
        )
        try:
            obj = model.objects.create()
            # Access document to trigger descriptor
            doc = obj.document
            assert isinstance(doc, LocalizedFileValue)

            # Each language should have a LocalizedFieldFile or similar
            for lang, _ in settings.LANGUAGES:
                file_obj = doc.get(lang)
                # Should be wrapped in LocalizedFieldFile
                if file_obj:
                    assert isinstance(file_obj, LocalizedFieldFile)
        finally:
            cleanup_fake_model(model)

    def test_save_form_data(self) -> None:
        """Test save_form_data method."""
        field = LocalizedFileField(upload_to="docs/", blank=True, null=True)
        field.name = "document"

        model = get_fake_model({"document": LocalizedFileField(blank=True, null=True)})
        try:
            instance = model()
            data = LocalizedFileValue({"en": None, "nl": None})
            field.save_form_data(instance, data)
            # Should set the attribute
            assert isinstance(instance.document, LocalizedFileValue)
        finally:
            cleanup_fake_model(model)


@pytest.mark.django_db(transaction=True)
class TestLocalizedFieldFile:
    """Tests for LocalizedFieldFile."""

    def test_initialization(self) -> None:
        """Test LocalizedFieldFile initialization."""
        model = get_fake_model(
            {"document": LocalizedFileField(upload_to="docs/", blank=True, null=True)}
        )
        try:
            instance = model()
            field = model._meta.get_field("document")
            file = LocalizedFieldFile(instance, field, "test.txt", "en")

            assert file.lang == "en"
            assert file.name == "test.txt"
        finally:
            cleanup_fake_model(model)

    def test_save_file(self) -> None:
        """Test LocalizedFieldFile.save() method."""
        model = get_fake_model(
            {"document": LocalizedFileField(upload_to="docs/{lang}/", blank=True, null=True)}
        )
        try:
            instance = model.objects.create()
            field = model._meta.get_field("document")

            # Create a file object
            content = ContentFile(b"Test content")
            file = LocalizedFieldFile(instance, field, None, "en")

            # Save the file
            file.save("test.txt", content, save=False)

            # File should be saved
            assert file.name
            assert "docs/en/" in file.name
            assert file._committed is True

            # Clean up
            file.delete(save=False)
        finally:
            cleanup_fake_model(model)

    def test_save_file_with_save_true(self) -> None:
        """Test LocalizedFieldFile.save() with save=True."""
        model = get_fake_model(
            {"document": LocalizedFileField(upload_to="docs/{lang}/", blank=True, null=True)}
        )
        try:
            instance = model.objects.create()
            field = model._meta.get_field("document")

            # Create a file object
            content = ContentFile(b"Test content")
            file = LocalizedFieldFile(instance, field, None, "en")

            # Save the file with save=True
            file.save("test_save.txt", content, save=True)

            # Instance should be saved
            instance.refresh_from_db()
            assert file.name

            # Clean up
            file.delete(save=False)
        finally:
            cleanup_fake_model(model)

    def test_delete_file(self) -> None:
        """Test LocalizedFieldFile.delete() method."""
        model = get_fake_model(
            {"document": LocalizedFileField(upload_to="docs/{lang}/", blank=True, null=True)}
        )
        try:
            instance = model.objects.create()
            field = model._meta.get_field("document")

            # Create and save a file
            content = ContentFile(b"Test content")
            file = LocalizedFieldFile(instance, field, None, "en")
            file.save("test_delete.txt", content, save=False)

            filename = file.name
            assert file.storage.exists(filename)

            # Delete the file
            file.delete(save=False)

            # File should be deleted
            assert not file.storage.exists(filename)
            assert file.name is None
            assert file._committed is False
        finally:
            cleanup_fake_model(model)

    def test_delete_file_with_save_true(self) -> None:
        """Test LocalizedFieldFile.delete() with save=True."""
        model = get_fake_model(
            {"document": LocalizedFileField(upload_to="docs/{lang}/", blank=True, null=True)}
        )
        try:
            instance = model.objects.create()
            field = model._meta.get_field("document")

            # Create and save a file
            content = ContentFile(b"Test content")
            file = LocalizedFieldFile(instance, field, None, "en")
            file.save("test_delete_save.txt", content, save=False)

            # Delete the file with save=True
            file.delete(save=True)

            # Instance should be saved
            instance.refresh_from_db()
            assert file.name is None
        finally:
            cleanup_fake_model(model)

    def test_delete_empty_file(self) -> None:
        """Test deleting an empty file does nothing."""
        model = get_fake_model(
            {"document": LocalizedFileField(upload_to="docs/{lang}/", blank=True, null=True)}
        )
        try:
            instance = model()
            field = model._meta.get_field("document")

            # Create an empty file
            file = LocalizedFieldFile(instance, field, None, "en")

            # Delete should do nothing for empty file
            file.delete(save=False)  # Should not raise
        finally:
            cleanup_fake_model(model)


@pytest.mark.django_db(transaction=True)
class TestLocalizedFileValueDescriptor:
    """Tests for LocalizedFileValueDescriptor."""

    def test_get_wraps_string_values(self) -> None:
        """Test descriptor wraps string file paths."""
        model = get_fake_model(
            {"document": LocalizedFileField(upload_to="docs/", blank=True, null=True)}
        )
        try:
            obj = model()
            # Manually set a string value
            obj.__dict__["document"] = LocalizedFileValue({"en": "path/to/file.txt"})

            # Access through descriptor
            doc = obj.document
            en_file = doc.get("en")

            # Should be wrapped
            assert isinstance(en_file, LocalizedFieldFile)
            assert en_file.lang == "en"
        finally:
            cleanup_fake_model(model)

    def test_get_returns_descriptor_on_class(self) -> None:
        """Test descriptor returns self when accessed on class."""
        model = get_fake_model(
            {"document": LocalizedFileField(upload_to="docs/", blank=True, null=True)}
        )
        try:
            descriptor = model.document
            assert isinstance(descriptor, LocalizedFileValueDescriptor)
        finally:
            cleanup_fake_model(model)
