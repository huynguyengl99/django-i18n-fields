"""
Configuration settings for django-i18n-fields package.

This module provides a centralized configuration system for i18n_fields,
using Django's standard settings pattern.
"""

from typing import Any, Literal

from django.conf import settings
from django.core.signals import setting_changed


class I18nFieldsDefaults:
    """Default settings for i18n_fields package."""

    # Admin display mode: "tab" or "dropdown"
    DISPLAY: Literal["tab", "dropdown"] = "tab"

    # Language fallback chains
    # Example: {"nl": ["en"], "fr": ["en"]}
    FALLBACKS: dict[str, list[str]] = {}

    # Max retries for unique slug generation
    MAX_RETRIES: int = 100

    # Enable automatic lookup registration
    REGISTER_LOOKUPS: bool = True


class I18nFieldsSettings:
    """
    Settings object that provides access to i18n_fields settings.

    Settings are accessed via the I18N_FIELDS dict in Django settings.
    """

    def __init__(
        self,
        user_settings: dict[str, Any] | None = None,
        defaults: type | None = None,
    ):
        self._user_settings = user_settings or {}
        self._defaults = defaults or I18nFieldsDefaults
        self._cached_attrs: set[str] = set()

    @property
    def user_settings(self) -> dict[str, Any]:
        if not hasattr(self, "_user_settings_loaded"):
            self._user_settings = (  # pyright: ignore[reportUnknownMemberType]
                getattr(settings, "I18N_FIELDS", None) or {}
            )
            self._user_settings_loaded = True
        return self._user_settings

    def __getattr__(self, attr: str) -> Any:
        if attr.startswith("_"):
            raise AttributeError(f"Invalid setting: '{attr}'")

        # Check user settings first
        if attr in self.user_settings:
            val = self.user_settings[attr]
        elif hasattr(self._defaults, attr):
            val = getattr(self._defaults, attr)
        else:
            raise AttributeError(f"Invalid i18n_fields setting: '{attr}'")

        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self) -> None:
        """Reload settings from Django settings."""
        for attr in self._cached_attrs:
            try:
                delattr(self, attr)
            except AttributeError:
                pass
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings_loaded"):
            delattr(self, "_user_settings_loaded")
        self._user_settings = {}


i18n_fields_settings = I18nFieldsSettings()


def reload_settings(*args: Any, **kwargs: Any) -> None:
    """Reload settings when Django settings change."""
    setting = kwargs.get("setting")
    if setting == "I18N_FIELDS":
        i18n_fields_settings.reload()


setting_changed.connect(reload_settings)  # pyright: ignore[reportUnknownMemberType]
