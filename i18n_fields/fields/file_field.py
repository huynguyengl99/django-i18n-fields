"""LocalizedFileField for file uploads in multiple languages."""

import datetime
import json
import posixpath
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from django.core.files import File
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils.encoding import force_str

from ..descriptor import LocalizedValueDescriptor
from ..value import LocalizedFileValue, LocalizedValue
from .field import LocalizedField

if TYPE_CHECKING:
    from django.core.files.storage import Storage  # noqa


class LocalizedFieldFile(FieldFile):
    """FieldFile subclass that tracks language for localized file fields."""

    lang: str

    def __init__(
        self,
        instance: models.Model,
        field: "LocalizedFileField",
        name: str | None,
        lang: str,
    ):
        """Initialize the file.

        Args:
            instance: The model instance.
            field: The file field.
            name: The file name.
            lang: The language code.
        """
        super().__init__(instance, field, name)  # type: ignore[arg-type]
        self.lang = lang

    def save(self, name: str, content: "File[Any]", save: bool = True) -> None:
        """Save the file.

        Args:
            name: The file name.
            content: The file content.
            save: Whether to save the model instance.
        """
        name = self.field.generate_filename(self.instance, name, self.lang)  # type: ignore[call-arg]
        self.name = self.storage.save(
            name,  # pyright: ignore
            content,
            max_length=self.field.max_length,
        )
        self._committed = True

        if save:
            self.instance.save()

    save.alters_data = True  # type: ignore[attr-defined]

    def delete(self, save: bool = True) -> None:
        """Delete the file.

        Args:
            save: Whether to save the model instance after deletion.
        """
        if not self:
            return

        if hasattr(self, "_file"):
            self.close()
            del self.file

        if self.name:
            self.storage.delete(self.name)
        self.name = None
        self._committed = False

        if save:
            self.instance.save()

    delete.alters_data = True  # type: ignore[attr-defined]


class LocalizedFileValueDescriptor(LocalizedValueDescriptor[LocalizedFileValue]):
    """Descriptor for LocalizedFileField that wraps file values."""

    field: "LocalizedFileField"

    def __get__(
        self,
        instance: models.Model | None,
        cls: type[models.Model] | None = None,
    ) -> "LocalizedFileValue | LocalizedFileValueDescriptor":
        """Get the LocalizedFileValue with wrapped file objects.

        Args:
            instance: The model instance.
            cls: The model class.

        Returns:
            LocalizedFileValue with wrapped files.
        """
        raw_value = super().__get__(instance, cls)

        if instance is None:
            return raw_value  # type: ignore[return-value]

        assert not isinstance(raw_value, LocalizedValueDescriptor)
        value: LocalizedFileValue = raw_value

        for lang, file in value.__dict__.items():
            if isinstance(file, str) or file is None:
                file_obj = self.field.value_class(instance, self.field, file, lang)
                value.set(lang, file_obj)

            elif isinstance(file, File) and not isinstance(file, LocalizedFieldFile):
                file_copy = self.field.value_class(
                    instance, self.field, file.name, lang
                )
                file_copy.file = file
                file_copy._committed = False  # pyright: ignore[reportPrivateUsage]
                value.set(lang, file_copy)

            elif isinstance(file, LocalizedFieldFile) and not hasattr(file, "field"):
                file.instance = instance
                file.field = self.field
                file.storage = self.field.storage
                file.lang = lang

            elif isinstance(file, LocalizedFieldFile) and instance is not file.instance:
                file.instance = instance
                file.lang = lang

        return value


class LocalizedFileField(LocalizedField[LocalizedFileValue]):
    """Localized field for file uploads.

    Each language can have a different uploaded file.

    Example:
        class Document(models.Model):
            file = LocalizedFileField(upload_to='documents/{lang}/')
    """

    descriptor_class: type[LocalizedFileValueDescriptor] = (  # pyright: ignore
        LocalizedFileValueDescriptor
    )
    attr_class: type[LocalizedFileValue] = LocalizedFileValue
    value_class = LocalizedFieldFile

    def __init__(
        self,
        verbose_name: str | None = None,
        name: str | None = None,
        upload_to: str | Callable[..., str] = "",
        storage: "Storage | None" = None,
        **kwargs: Any,
    ):
        """Initialize the file field.

        Args:
            verbose_name: Human-readable name.
            name: Field name.
            upload_to: Upload path or callable.
            storage: Storage backend.
            **kwargs: Additional field arguments.
        """
        self.storage = storage or default_storage
        self.upload_to = upload_to

        super().__init__(verbose_name, name, **kwargs)

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        """Deconstruct the field for migrations.

        Returns:
            Tuple of (name, path, args, kwargs).
        """
        name, path, args, kwargs = super().deconstruct()
        kwargs["upload_to"] = self.upload_to
        if self.storage is not default_storage:
            kwargs["storage"] = self.storage
        return name, path, args, kwargs

    def get_prep_value(  # type: ignore[override]
        self, value: LocalizedValue | None
    ) -> dict[str, Any] | None:
        """Prepare value for database storage.

        Args:
            value: The value to prepare.

        Returns:
            Dictionary with file paths for JSON storage.
        """
        if isinstance(value, LocalizedValue):
            prep_value = LocalizedValue()
            for k, v in value.__dict__.items():
                if v is None:
                    prep_value.set(k, "")
                else:
                    prep_value.set(k, str(v))
            result = super().get_prep_value(prep_value)
            return result if isinstance(result, dict) else None
        result = super().get_prep_value(value)
        return result if isinstance(result, dict) else None

    def pre_save(self, model_instance: models.Model, add: bool) -> Any:
        """Save uncommitted files before model save.

        Args:
            model_instance: The model instance being saved.
            add: Whether this is a new instance.

        Returns:
            The field value.
        """
        value = super().pre_save(model_instance, add)
        if isinstance(value, LocalizedValue):
            for file in value.__dict__.values():
                if file and hasattr(file, "_committed") and not file._committed:
                    file.save(file.name, file, save=False)
        return value

    def generate_filename(
        self,
        instance: models.Model,
        filename: str,
        lang: str,
    ) -> str:
        """Generate the filename for upload.

        Args:
            instance: The model instance.
            filename: Original filename.
            lang: Language code.

        Returns:
            Generated filename.
        """
        if callable(self.upload_to):
            filename = self.upload_to(instance, filename, lang)
        else:
            now = datetime.datetime.now()
            dirname = force_str(now.strftime(force_str(self.upload_to)))
            dirname = dirname.format(lang=lang)
            filename = posixpath.join(dirname, filename)
        return self.storage.generate_filename(filename)

    def save_form_data(
        self,
        instance: models.Model,
        data: LocalizedValue | None,
    ) -> None:
        """Save form data to the model instance.

        Args:
            instance: The model instance.
            data: The form data.
        """
        if isinstance(data, LocalizedValue):
            for k, v in data.__dict__.items():
                if v is not None and not v:
                    data.set(k, "")
            setattr(instance, self.name, data)

    def formfield(self, **kwargs: Any) -> Any:  # type: ignore[override]
        """Get the form field for this field.

        Args:
            **kwargs: Keyword arguments for the form field.

        Returns:
            The form field instance.
        """
        from ..forms import LocalizedFileFieldForm

        defaults = {"form_class": LocalizedFileFieldForm}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def value_to_string(self, obj: models.Model) -> str:
        """Serialize the field value to string.

        Args:
            obj: The model instance.

        Returns:
            JSON string of file paths.
        """
        value = self.value_from_object(obj)
        if isinstance(value, LocalizedFileValue):
            return json.dumps({k: v.name for k, v in value.__dict__.items()})
        return super().value_to_string(obj)
