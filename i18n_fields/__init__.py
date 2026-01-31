"""
django-i18n-fields - Localized model fields for Django.

A Django package that provides model fields for storing values in multiple languages
using JSONField (database-agnostic).

Example:
    from django.db import models
    from i18n_fields.fields import LocalizedCharField, LocalizedTextField

    class Article(models.Model):
        title = LocalizedCharField(required=['en'])
        content = LocalizedTextField(blank=True)

Settings (in settings.py):
    I18N_FIELDS = {
        "DISPLAY": "tab",  # or "dropdown" for admin widgets
        "FALLBACKS": {"nl": ["en"], "fr": ["en"]},  # Language fallback chains
        "MAX_RETRIES": 100,  # Max retries for unique slug generation
        "REGISTER_LOOKUPS": True,  # Auto-register query lookups
    }
"""

from .admin import LocalizedFieldsAdmin, LocalizedFieldsAdminMixin
from .expressions import L, LocalizedRef
from .fields import (
    LocalizedBooleanField,
    LocalizedCharField,
    LocalizedField,
    LocalizedFileField,
    LocalizedFloatField,
    LocalizedIntegerField,
    LocalizedTextField,
    LocalizedUniqueSlugField,
)
from .mixins import AtomicSlugRetryMixin
from .settings import i18n_fields_settings
from .value import (
    LocalizedBooleanValue,
    LocalizedFileValue,
    LocalizedFloatValue,
    LocalizedIntegerValue,
    LocalizedStringValue,
    LocalizedValue,
)

__all__ = [
    # Fields
    "LocalizedField",
    "LocalizedCharField",
    "LocalizedTextField",
    "LocalizedIntegerField",
    "LocalizedFloatField",
    "LocalizedBooleanField",
    "LocalizedFileField",
    "LocalizedUniqueSlugField",
    # Values
    "LocalizedValue",
    "LocalizedStringValue",
    "LocalizedIntegerValue",
    "LocalizedFloatValue",
    "LocalizedBooleanValue",
    "LocalizedFileValue",
    # Admin
    "LocalizedFieldsAdminMixin",
    "LocalizedFieldsAdmin",
    # Mixins
    "AtomicSlugRetryMixin",
    # Expressions
    "LocalizedRef",
    "L",
    # Settings
    "i18n_fields_settings",
]

__version__ = "0.1.0"
default_app_config = "i18n_fields.apps.I18nFieldsConfig"
