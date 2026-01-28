"""Descriptors for localized field attributes."""

import json
from typing import TYPE_CHECKING, Any, Generic, cast

from django.conf import settings
from django.utils import translation

from typing_extensions import TypeVar

from .value import LocalizedValue

if TYPE_CHECKING:
    from django.db import models

    from .fields.field import LocalizedField

ValueT = TypeVar("ValueT", bound=LocalizedValue, default=LocalizedValue)


class LocalizedValueDescriptor(Generic[ValueT]):
    """Descriptor for accessing LocalizedValue on model instances.

    Allows setting values in the active language via string assignment:
        >>> instance.title = "English title"  # Sets for active language

    And accessing values in specific languages:
        >>> instance.title.en = "English"
        >>> instance.title.fr = "French"
    """

    def __init__(self, field: "LocalizedField[ValueT]"):
        """Initialize the descriptor.

        Args:
            field: The LocalizedField this descriptor is attached to.
        """
        self.field = field

    def __get__(
        self,
        instance: "models.Model | None",
        cls: type["models.Model"] | None = None,
    ) -> ValueT | "LocalizedValueDescriptor[ValueT]":
        """Get the LocalizedValue from the instance.

        Args:
            instance: The model instance.
            cls: The model class.

        Returns:
            The LocalizedValue, or self if accessed on the class.
        """
        if instance is None:
            return self

        if self.field.name in instance.__dict__:
            value = instance.__dict__[self.field.name]
        elif not instance._state.adding:
            instance.refresh_from_db(fields=[self.field.name])
            value = getattr(instance, self.field.name)
        else:
            value = None

        # Already a LocalizedValue - return as-is
        if isinstance(value, self.field.attr_class):
            return value

        # Convert None to empty LocalizedValue
        if value is None:
            value = self.field.attr_class()
            instance.__dict__[self.field.name] = (  # pyright: ignore[reportIndexIssue]
                value
            )
            return value

        # Convert JSON string to LocalizedValue
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                # Not valid JSON - create LocalizedValue with this as default lang value
                value = self.field.attr_class({settings.LANGUAGE_CODE: value})
                instance.__dict__[self.field.name] = value  # pyright: ignore
                return value

        # Convert dict to LocalizedValue
        if isinstance(value, dict):
            value = self.field.attr_class(cast(dict[str, Any], value))
            instance.__dict__[self.field.name] = (  # pyright: ignore[reportIndexIssue]
                value
            )
            return value

        # Fallback - return as-is (shouldn't happen)
        return value  # type: ignore[no-any-return]

    def __set__(self, instance: "models.Model", value: Any) -> None:
        """Set the LocalizedValue on the instance.

        If a string is assigned, it sets the value for the active language.
        Otherwise, it sets the entire value.

        Args:
            instance: The model instance.
            value: The value to set.
        """
        if isinstance(value, str):
            language = translation.get_language() or settings.LANGUAGE_CODE
            current_value = self.__get__(instance, None)
            assert not isinstance(current_value, LocalizedValueDescriptor)
            current_value.set(language, value)
        else:
            instance.__dict__[self.field.name] = (  # pyright: ignore[reportIndexIssue]
                value
            )
