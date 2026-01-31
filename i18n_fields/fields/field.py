"""Base LocalizedField using JSONField."""

import json
from typing import Any, Generic, cast

from django.conf import settings
from django.db import models
from django.db.utils import IntegrityError

from typing_extensions import TypeVar

from ..descriptor import LocalizedValueDescriptor
from ..forms import LocalizedFieldForm
from ..value import LocalizedValue

ValueT = TypeVar("ValueT", bound=LocalizedValue, default=LocalizedValue)


class LocalizedField(models.JSONField, Generic[ValueT]):
    """A field that stores localized values in multiple languages.

    Internally stored as a JSONField with a key for each language code.
    Works with all databases that support JSONField (PostgreSQL, MySQL, SQLite, etc.).

    Example:
        class Article(models.Model):
            title = LocalizedField(required=['en'])
            description = LocalizedField(blank=True)
    """

    attr_class: type[ValueT] = LocalizedValue  # type: ignore[assignment]
    descriptor_class: type[LocalizedValueDescriptor[ValueT]] = LocalizedValueDescriptor

    def __init__(
        self,
        *args: Any,
        required: bool | list[str] | None = None,
        blank: bool = False,
        **kwargs: Any,
    ):
        """Initialize the LocalizedField.

        Args:
            required: Languages that require a value.
                - None with blank=True: No languages required
                - None with blank=False: Primary language required
                - True: All languages required
                - False: No languages required
                - List[str]: Specific languages required
            blank: Whether all language values can be empty.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        if (required is None and blank) or required is False:
            self.required: list[str] = []
        elif required is None and not blank:
            self.required = [settings.LANGUAGE_CODE]
        elif required is True:
            self.required = [lang_code for lang_code, _ in settings.LANGUAGES]
        else:
            self.required = required  # type: ignore[assignment]

        super().__init__(*args, blank=blank, **kwargs)

    def contribute_to_class(
        self,
        cls: type[models.Model],
        name: str,
        private_only: bool = False,
    ) -> None:
        """Add this field to the model class.

        Args:
            cls: The model class.
            name: The field name.
            private_only: Whether this is a private field.
        """
        super().contribute_to_class(cls, name, private_only=private_only)
        setattr(cls, self.name, self.descriptor_class(self))

    def from_db_value(
        self,
        value: dict[str, Any] | list[Any] | str | bool | None,
        expression: Any,
        connection: Any,
    ) -> ValueT | list[Any] | str | bool | None:
        """Convert database value to Python LocalizedValue.

        Args:
            value: The value from the database.
            expression: The expression being evaluated.
            connection: The database connection.

        Returns:
            LocalizedValue instance or appropriate type for expressions.
        """
        if value is None:
            return None

        # Handle boolean values (from BooleanField or key transforms)
        if isinstance(value, bool):
            return value

        # Handle JSON string from database (SQLite returns strings)
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                # If it's not valid JSON, it might be a simple string value
                # from a key transform - return as-is
                return value  # type: ignore[return-value]

        # Handle list from aggregation expressions
        if isinstance(value, list):
            result: list[Any] = []
            for inner_val in value:
                if isinstance(inner_val, dict):
                    result.append(
                        self.attr_class(cast(dict[str, Any], inner_val))
                        if inner_val
                        else None
                    )
                else:
                    result.append(inner_val)
            return result

        # Handle dict value
        if isinstance(value, dict):
            return self.attr_class(value)

        # Other types (int, float, bool) from key transforms
        return value

    def to_python(self, value: dict[str, Any] | str | None) -> ValueT:
        """Convert value to Python LocalizedValue.

        Args:
            value: The value to convert.

        Returns:
            LocalizedValue instance.
        """
        # If it's a JSON string, parse it first
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Not valid JSON, let parent handle it
                pass

        deserialized = super().to_python(value)

        if not deserialized:
            return self.attr_class()

        return self.attr_class(deserialized)

    def get_prep_value(
        self, value: ValueT | dict[str, Any] | str | int | float | bool | None
    ) -> dict[str, Any] | str | int | float | bool | None:
        """Prepare value for database storage.

        Args:
            value: The LocalizedValue to prepare.

        Returns:
            Dictionary ready for JSON storage or the original value for lookups.
        """
        # For lookups (e.g., name__en="Technology"), value might be a plain string, number, or boolean
        # Pass through simple scalar types that are valid for JSON lookups
        if isinstance(value, str | int | float | bool):
            return value

        # Value is now dict[str, Any] | ValueT | None
        if isinstance(value, dict) and not isinstance(value, LocalizedValue):
            value = self.attr_class(value)
        elif (
            value is not None
            and not isinstance(  # pyright: ignore[reportUnnecessaryIsInstance]
                value, LocalizedValue
            )
        ):
            # Handle invalid types (like lists) - return None
            return None

        # Use 'is not None' instead of truthiness to handle falsy values like False, 0, empty strings
        if value is not None:
            cleaned_value = self.clean(value)  # type: ignore[arg-type]
            self.validate(cleaned_value)
        else:
            cleaned_value = value

        # Use 'is not None' instead of truthiness to handle falsy LocalizedValue instances
        return dict(cleaned_value) if cleaned_value is not None else None

    def clean(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, value: ValueT | None, *args: Any
    ) -> ValueT | None:
        """Clean the value for database storage.

        Converts all-null values to None if null=True.

        Args:
            value: The value to clean.
            *args: Additional arguments.

        Returns:
            Cleaned value or None.
        """
        # Check for None explicitly to handle falsy LocalizedValue instances (e.g., LocalizedBooleanValue with False)
        if value is None:
            return None

        # value is now LocalizedValue
        is_all_null = True
        for lang_code, _ in settings.LANGUAGES:
            if value.get(lang_code) is not None:
                is_all_null = False
                break

        if is_all_null and self.null:
            return None

        return value

    def validate(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, value: ValueT | None, *args: Any
    ) -> None:
        """Validate required languages have values.

        Args:
            value: The value to validate.
            *args: Additional arguments.

        Raises:
            IntegrityError: If a required language is missing a value.
        """
        if self.null:
            return

        if not value:
            return

        for lang in self.required:
            lang_val = value.get(lang)

            if lang_val is None:
                raise IntegrityError(
                    f'null value in column "{self.name}.{lang}" violates not-null constraint'
                )

    def formfield(self, **kwargs: Any) -> Any:  # type: ignore[override]
        """Get the form field for this field.

        Args:
            **kwargs: Keyword arguments for the form field.

        Returns:
            The form field instance.
        """
        # Remove JSONField-specific kwargs that our form doesn't accept
        kwargs.pop("encoder", None)
        kwargs.pop("decoder", None)

        # Set form_class and required explicitly to avoid type confusion
        kwargs.setdefault("form_class", LocalizedFieldForm)
        kwargs.setdefault("required", False if self.blank else self.required)

        # Don't call JSONField's formfield, skip to parent
        return models.Field.formfield(  # pyright: ignore[reportUnknownMemberType]
            self, **kwargs
        )

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        """Deconstruct the field for migrations.

        Returns:
            Tuple of (name, path, args, kwargs).
        """
        name, path, args, kwargs = super().deconstruct()
        if self.required:
            kwargs["required"] = self.required
        return name, path, list(args), dict(kwargs)
