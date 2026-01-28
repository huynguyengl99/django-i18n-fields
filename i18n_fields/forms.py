"""Form classes for localized fields."""

from typing import Any

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.widgets import FILE_INPUT_CONTRADICTION

from .value import (
    LocalizedBooleanValue,
    LocalizedFileValue,
    LocalizedFloatValue,
    LocalizedIntegerValue,
    LocalizedStringValue,
    LocalizedValue,
)
from .widgets import (
    LocalizedCharFieldWidget,
    LocalizedFieldWidget,
    LocalizedFileWidget,
)


class LocalizedFieldForm(forms.MultiValueField):
    """Form field for editing localized values in multiple languages."""

    widget = LocalizedFieldWidget
    field_class = forms.fields.CharField
    value_class = LocalizedValue

    def __init__(
        self,
        *args: Any,
        required: bool | list[str] = False,
        **kwargs: Any,
    ):
        """Initialize the form field.

        Args:
            required: Whether field is required. Can be bool or list of
                language codes.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        fields: list[forms.Field] = []

        # Don't show hidden initial input
        kwargs["show_hidden_initial"] = False

        for lang_code, _ in settings.LANGUAGES:
            field_options: dict[str, Any] = {
                "required": (
                    required if isinstance(required, bool) else (lang_code in required)
                ),
                "label": lang_code,
            }
            fields.append(self.field_class(**field_options))

        super().__init__(
            fields,
            *args,
            required=required if isinstance(required, bool) else True,
            require_all_fields=False,
            **kwargs,
        )

        # After super().__init__, MultiValueField replaces widget.widgets
        # with the individual field widgets. We need to re-apply the
        # language attributes to these new widgets.
        for (lang_code, lang_name), field, widget in zip(
            settings.LANGUAGES, self.fields, self.widget.widgets, strict=False
        ):
            widget.attrs["lang"] = lang_code
            widget.lang_code = lang_code  # type: ignore[attr-defined]
            widget.lang_name = lang_name  # type: ignore[attr-defined]
            widget.is_required = field.required

    def compress(self, data_list: list[Any]) -> LocalizedValue:
        """Compress values from individual fields into LocalizedValue.

        Args:
            data_list: Values from all language widgets.

        Returns:
            LocalizedValue containing all language values.
        """
        localized_value = self.value_class()

        for (lang_code, _), val in zip(settings.LANGUAGES, data_list, strict=False):
            localized_value.set(lang_code, val)

        return localized_value


class LocalizedCharFieldForm(LocalizedFieldForm):
    """Form field for LocalizedCharField."""

    widget = LocalizedCharFieldWidget
    value_class = LocalizedStringValue


class LocalizedTextFieldForm(LocalizedFieldForm):
    """Form field for LocalizedTextField."""

    value_class = LocalizedStringValue


class LocalizedIntegerFieldForm(LocalizedFieldForm):
    """Form field for LocalizedIntegerField."""

    field_class = forms.fields.IntegerField  # type: ignore[assignment]
    value_class = LocalizedIntegerValue


class LocalizedFloatFieldForm(LocalizedFieldForm):
    """Form field for LocalizedFloatField."""

    field_class = forms.fields.FloatField  # type: ignore[assignment]
    value_class = LocalizedFloatValue


class LocalizedBooleanFieldForm(LocalizedFieldForm, forms.BooleanField):
    """Form field for LocalizedBooleanField."""

    field_class = forms.fields.NullBooleanField  # type: ignore[assignment]
    value_class = LocalizedBooleanValue


class LocalizedFileFieldForm(LocalizedFieldForm, forms.FileField):
    """Form field for LocalizedFileField."""

    widget = LocalizedFileWidget
    field_class = forms.fields.FileField  # type: ignore[assignment]
    value_class = LocalizedFileValue

    def clean(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, data: list[Any], initial: Any = None
    ) -> LocalizedValue:
        """Clean the file field values.

        Args:
            data: Values from all language widgets.
            initial: Initial values.

        Returns:
            LocalizedValue containing all file values.

        Raises:
            ValidationError: If validation fails.
        """
        if initial is None:
            initial = [None for _ in range(len(data))]
        elif not isinstance(initial, list):
            initial = self.widget.decompress(initial)  # type: ignore[call-arg]

        clean_data: list[Any] = []
        errors: list[Any] = []

        if not data or isinstance(
            data, list | tuple
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            is_empty = [v for v in data if v not in self.empty_values]
            if (not data or not is_empty) and (not initial or not is_empty):
                if self.required:
                    raise ValidationError(
                        self.error_messages["required"], code="required"
                    )
        else:
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        for i, field in enumerate(self.fields):
            try:
                field_value = data[i]
            except IndexError:
                field_value = None

            field_initial: Any
            try:
                field_initial = initial[i]  # pyright: ignore[reportUnknownVariableType]
            except IndexError:
                field_initial = None

            if field_value in self.empty_values and field_initial in self.empty_values:
                if self.require_all_fields:
                    if self.required:
                        raise ValidationError(
                            self.error_messages["required"], code="required"
                        )
                elif field.required:
                    if field.error_messages["incomplete"] not in errors:
                        errors.append(field.error_messages["incomplete"])
                    continue
            try:
                clean_data.append(field.clean(field_value, field_initial))  # type: ignore[call-arg]
            except ValidationError as e:
                errors.extend(m for m in e.error_list if m not in errors)

        if errors:
            raise ValidationError(errors)

        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)
        return out

    def bound_data(self, data: Any | None, initial: Any) -> list[Any]:
        """Get bound data for the form field.

        Args:
            data: Form data.
            initial: Initial values.

        Returns:
            Bound data list.
        """
        # Ensure data is a list
        if not isinstance(data, list):
            return []

        data_list: list[Any] = data  # pyright: ignore[reportUnknownVariableType]
        bound_data: list[Any] = []
        if initial is None:
            initial = [None for _ in range(len(data_list))]
        elif not isinstance(initial, list):
            initial = self.widget.decompress(initial)  # type: ignore[call-arg]

        d: Any
        i: Any
        for d, i in zip(  # pyright: ignore[reportUnknownVariableType]
            data_list,
            initial,  # pyright: ignore
            strict=False,
        ):
            if d in (None, FILE_INPUT_CONTRADICTION):
                bound_data.append(i)
            else:
                bound_data.append(d)
        return bound_data
