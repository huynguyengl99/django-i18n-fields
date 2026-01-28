"""Localized field classes for Django models."""

from .boolean_field import LocalizedBooleanField
from .char_field import LocalizedCharField
from .field import LocalizedField
from .file_field import LocalizedFileField
from .float_field import LocalizedFloatField
from .integer_field import LocalizedIntegerField
from .text_field import LocalizedTextField
from .uniqueslug_field import LocalizedUniqueSlugField

__all__ = [
    "LocalizedField",
    "LocalizedCharField",
    "LocalizedTextField",
    "LocalizedIntegerField",
    "LocalizedFloatField",
    "LocalizedBooleanField",
    "LocalizedFileField",
    "LocalizedUniqueSlugField",
]
