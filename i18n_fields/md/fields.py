"""LocalizedMartorField for markdown editing with martor."""

from typing import Any

from ..fields.field import LocalizedField
from ..value import LocalizedStringValue
from .forms import LocalizedMartorForm
from .widgets import AdminLocalizedMartorWidget


class LocalizedMartorField(LocalizedField[LocalizedStringValue]):
    """Localized field for markdown text using martor editor.

    Uses LocalizedStringValue which defaults to empty string.
    Requires the 'martor' package to be installed.

    Example:
        class Article(models.Model):
            content = LocalizedMartorField(blank=True)
    """

    attr_class: type[LocalizedStringValue] = LocalizedStringValue

    def formfield(self, **kwargs: Any) -> Any:  # type: ignore[override]
        """Get the form field for this field.

        Args:
            **kwargs: Keyword arguments for the form field.

        Returns:
            The form field instance.
        """
        # Extract display_mode from widget if provided
        display_mode = None
        widget = kwargs.pop("widget", None)
        if widget and hasattr(widget, "display_mode"):
            display_mode = widget.display_mode

        # Create our martor widget with the display mode
        martor_widget = AdminLocalizedMartorWidget
        if display_mode:
            # If display_mode was passed, create instance with it
            martor_widget = AdminLocalizedMartorWidget(display_mode=display_mode)  # type: ignore[assignment]

        defaults = {
            "form_class": LocalizedMartorForm,
            "widget": martor_widget,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
