"""Utility functions for i18n_fields."""

from typing import Any

from django.conf import settings


def get_language_codes() -> list[str]:
    """Get a list of all configured language codes.

    Returns:
        List of language codes from settings.LANGUAGES.
    """
    return [lang_code for lang_code, _ in settings.LANGUAGES]


def resolve_object_property(obj: Any, path: str) -> Any:
    """Resolve a nested property path on an object.

    Example:
        resolve_object_property(obj, 'other.field.name')
        # Equivalent to obj.other.field.name

    Args:
        obj: The object to resolve the property on.
        path: Dot-separated path to the property.

    Returns:
        The resolved value.

    Raises:
        AttributeError: If any part of the path cannot be resolved.
    """
    value = obj
    for path_part in path.split("."):
        value = getattr(value, path_part)
    return value
