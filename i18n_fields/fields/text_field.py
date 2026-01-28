"""LocalizedTextField for long text in multiple languages."""

from typing import Any

from .char_field import LocalizedCharField


class LocalizedTextField(LocalizedCharField):
    """Localized field for long text (like TextField).

    Uses LocalizedStringValue which defaults to empty string.

    Example:
        class Article(models.Model):
            content = LocalizedTextField(blank=True)
    """

    def formfield(self, **kwargs: Any) -> Any:  # type: ignore[override]
        """Get the form field for this field.

        Args:
            **kwargs: Keyword arguments for the form field.

        Returns:
            The form field instance.
        """
        from ..forms import LocalizedTextFieldForm

        defaults = {"form_class": LocalizedTextFieldForm}
        defaults.update(kwargs)
        return super().formfield(**defaults)
