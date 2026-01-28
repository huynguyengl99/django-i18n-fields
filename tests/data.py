"""Test data utilities for i18n_fields tests."""

from django.conf import settings


def get_init_values() -> dict[str, str]:
    """Get a test dictionary containing a value for each configured language.

    Returns:
        Dictionary mapping language codes to test values.
    """
    return {
        lang_code: f"value in {lang_name}"
        for lang_code, lang_name in settings.LANGUAGES
    }


def get_empty_values() -> dict[str, None]:
    """Get a dictionary with None values for each language.

    Returns:
        Dictionary mapping language codes to None.
    """
    return {lang_code: None for lang_code, _ in settings.LANGUAGES}


def get_primary_language_value(value: str) -> dict[str, str | None]:
    """Get a dictionary with a value only for the primary language.

    Args:
        value: The value to set for the primary language.

    Returns:
        Dictionary with value only for primary language.
    """
    result: dict[str, str | None] = {lang_code: None for lang_code, _ in settings.LANGUAGES}
    result[settings.LANGUAGE_CODE] = value
    return result
