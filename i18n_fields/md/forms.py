"""Form classes for localized martor fields."""

from martor.fields import MartorFormField  # pyright: ignore[reportMissingTypeStubs]

from ..forms import LocalizedFieldForm
from ..value import LocalizedStringValue
from .widgets import LocalizedMartorWidget


class LocalizedMartorForm(LocalizedFieldForm):
    """Form field for LocalizedMartorField with martor editor."""

    widget = LocalizedMartorWidget
    field_class = MartorFormField
    value_class = LocalizedStringValue
