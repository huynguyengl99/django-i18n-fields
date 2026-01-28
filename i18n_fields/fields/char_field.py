"""LocalizedCharField for short text in multiple languages."""

from typing import Any

from ..forms import LocalizedCharFieldForm
from ..value import LocalizedStringValue
from .field import LocalizedField


class LocalizedCharField(LocalizedField[LocalizedStringValue]):
    """Localized field for short text (like CharField).

    Uses LocalizedStringValue which defaults to empty string.

    Example:
        class Article(models.Model):
            title = LocalizedCharField(required=['en'])
    """

    attr_class: type[LocalizedStringValue] = LocalizedStringValue

    def formfield(self, **kwargs: Any) -> Any:  # type: ignore[override]
        """Get the form field for this field.

        Args:
            **kwargs: Keyword arguments for the form field.

        Returns:
            The form field instance.
        """
        defaults = {"form_class": LocalizedCharFieldForm}
        defaults.update(kwargs)
        return super().formfield(**defaults)
