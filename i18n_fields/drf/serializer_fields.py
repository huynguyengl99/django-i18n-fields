"""Custom DRF serializer fields for localized values."""

from typing import Any

from rest_framework.fields import (
    BooleanField,
    CharField,
    FileField,
    FloatField,
    IntegerField,
    SlugField,
)

from i18n_fields.value import LocalizedValue


class LocalizedCharField(CharField):
    """CharField that handles LocalizedValue objects by translating them."""

    def to_representation(self, value: Any) -> Any:
        """Translate LocalizedValue to current language string."""
        if isinstance(value, LocalizedValue):
            value = value.translate()
        # DRF's serializer handles None before calling to_representation,
        # but if translate() returns None, we should return it as-is
        if value is None:
            return None
        return super().to_representation(value)

    def to_internal_value(self, data: Any) -> Any:
        """Accept dict for input, pass string through to validation."""
        if isinstance(data, dict):
            # Accept dictionaries for localized content
            return data  # pyright: ignore[reportUnknownVariableType]
        # For non-dict values, use parent's validation
        return super().to_internal_value(data)


class LocalizedIntegerField(IntegerField):
    """IntegerField that handles LocalizedValue objects by translating them."""

    def to_representation(self, value: Any) -> Any:
        """Translate LocalizedValue to current language integer."""
        if isinstance(value, LocalizedValue):
            value = value.translate()
        if value is None:
            return None
        return super().to_representation(value)

    def to_internal_value(self, data: Any) -> Any:
        """Accept dict for input, pass other types through to validation."""
        if isinstance(data, dict):
            return data  # pyright: ignore[reportUnknownVariableType]
        return super().to_internal_value(data)


class LocalizedFloatField(FloatField):
    """FloatField that handles LocalizedValue objects by translating them."""

    def to_representation(self, value: Any) -> Any:
        """Translate LocalizedValue to current language float."""
        if isinstance(value, LocalizedValue):
            value = value.translate()
        if value is None:
            return None
        return super().to_representation(value)

    def to_internal_value(self, data: Any) -> Any:
        """Accept dict for input, pass other types through to validation."""
        if isinstance(data, dict):
            return data  # pyright: ignore[reportUnknownVariableType]
        return super().to_internal_value(data)


class LocalizedBooleanField(BooleanField):
    """BooleanField that handles LocalizedValue objects by translating them."""

    def to_representation(self, value: Any) -> Any:
        """Translate LocalizedValue to current language boolean."""
        if isinstance(value, LocalizedValue):
            value = value.translate()
        if value is None:
            return None
        return super().to_representation(value)

    def to_internal_value(self, data: Any) -> Any:
        """Accept dict for input, pass other types through to validation."""
        if isinstance(data, dict):
            return data  # pyright: ignore[reportUnknownVariableType]
        return super().to_internal_value(data)


class LocalizedSlugField(SlugField):
    """SlugField that handles LocalizedValue objects by translating them."""

    def to_representation(self, value: Any) -> Any:
        """Translate LocalizedValue to current language slug."""
        if isinstance(value, LocalizedValue):
            value = value.translate()
        if value is None:
            return None
        return super().to_representation(value)

    def to_internal_value(self, data: Any) -> Any:
        """Accept dict for input, pass other types through to validation."""
        if isinstance(data, dict):
            return data  # pyright: ignore[reportUnknownVariableType]
        return super().to_internal_value(data)


class LocalizedFileField(FileField):
    """FileField that handles LocalizedValue objects by translating them."""

    def to_representation(self, value: Any) -> Any:
        """Translate LocalizedValue to current language file."""
        if isinstance(value, LocalizedValue):
            value = value.translate()
        if value is None:
            return None
        return super().to_representation(  # pyright: ignore[reportUnknownMemberType]
            value
        )

    def to_internal_value(self, data: Any) -> Any:
        """Accept dict for input, pass other types through to validation."""
        if isinstance(data, dict):
            return data  # pyright: ignore[reportUnknownVariableType]
        return super().to_internal_value(  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            data
        )
