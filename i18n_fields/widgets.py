"""Widget classes for rendering localized fields in forms."""

import copy
from collections.abc import Mapping
from typing import Any

from django import forms
from django.conf import settings
from django.contrib.admin import widgets

from .settings import i18n_fields_settings
from .value import LocalizedValue


class LocalizedFieldWidget(forms.MultiWidget):
    """Widget that renders input for each language."""

    template_name = "i18n_fields/multiwidget.html"
    widget = forms.Textarea

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize widget with one sub-widget per language.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        initial_widgets = [copy.copy(self.widget) for _ in settings.LANGUAGES]
        super().__init__(initial_widgets, *args, **kwargs)

        for (lang_code, lang_name), widget in zip(
            settings.LANGUAGES, self.widgets, strict=False
        ):
            widget.attrs["lang"] = lang_code
            widget.lang_code = lang_code  # type: ignore[attr-defined]
            widget.lang_name = lang_name  # type: ignore[attr-defined]

    def value_from_datadict(
        self, data: Mapping[str, Any], files: Mapping[str, Any], name: str
    ) -> list[Any]:
        """Extract values from POST data using language codes.

        This overrides the default MultiWidget behavior to use language codes
        (like 'title_en', 'title_nl') instead of numeric indices.

        Args:
            data: Form data dictionary.
            files: Files dictionary.
            name: Base field name.

        Returns:
            List of values for each language.
        """
        values: list[Any] = []
        for lang_code, _ in settings.LANGUAGES:
            # Try language code suffix first (e.g., 'title_en')
            field_name = f"{name}_{lang_code}"
            value: Any = data.get(field_name)
            values.append(value)
        return values

    def value_omitted_from_data(
        self, data: Mapping[str, Any], files: Mapping[str, Any], name: str
    ) -> bool:
        """Check if any language field is present in the data.

        Args:
            data: Form data dictionary.
            files: Files dictionary.
            name: Base field name.

        Returns:
            True if all language fields are omitted, False otherwise.
        """
        for lang_code, _ in settings.LANGUAGES:
            field_name = f"{name}_{lang_code}"
            if field_name in data or field_name in files:
                return False
        return True

    def decompress(
        self, value: LocalizedValue | dict[str, Any] | str | None
    ) -> list[Any]:
        """Decompress LocalizedValue into list of values for each widget.

        Args:
            value: The LocalizedValue to decompress.

        Returns:
            List of values for each language widget.
        """
        if not value:
            return [None] * len(settings.LANGUAGES)

        # Handle string value (shouldn't happen but be defensive)
        if isinstance(value, str):
            import json

            try:
                value = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                # If it's a plain string, use it for the default language
                result: list[Any] = [None] * len(settings.LANGUAGES)
                for i, (lang_code, _) in enumerate(settings.LANGUAGES):
                    if lang_code == settings.LANGUAGE_CODE:
                        result[i] = value
                        break
                return result

        # Handle dict or LocalizedValue
        if isinstance(value, dict):
            result_list: list[Any] = []
            for lang_code, _ in settings.LANGUAGES:
                result_list.append(value.get(lang_code))
            return result_list

        # Fallback: return Nones
        return [None] * len(settings.LANGUAGES)

    def get_context(
        self, name: str, value: Any, attrs: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Get the template context for rendering.

        Args:
            name: Widget name.
            value: Current value.
            attrs: HTML attributes.

        Returns:
            Template context dictionary.
        """
        context = super(forms.MultiWidget, self).get_context(name, value, attrs)

        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized

        if not isinstance(value, list):
            value = self.decompress(value)

        final_attrs = context["widget"]["attrs"]
        input_type = final_attrs.pop("type", None)
        id_ = final_attrs.get("id")

        subwidgets: list[Any] = []
        for i, widget in enumerate(self.widgets):
            if input_type is not None:
                widget.input_type = input_type  # type: ignore[attr-defined]

            # Use language code for field name instead of index
            lang_code = widget.lang_code  # type: ignore[attr-defined]
            widget_name = f"{name}_{lang_code}"

            widget_value: Any
            try:
                widget_value = value[i]  # pyright: ignore[reportUnknownVariableType]
            except IndexError:
                widget_value = None

            widget_attrs: dict[str, Any]
            if id_:
                widget_attrs = final_attrs.copy()
                widget_attrs["id"] = f"{id_}_{lang_code}"
            else:
                widget_attrs = final_attrs

            widget_attrs = self.build_widget_attrs(widget, widget_value, widget_attrs)
            widget_context = widget.get_context(
                widget_name, widget_value, widget_attrs
            )["widget"]
            widget_context.update(
                {
                    "lang_code": widget.lang_code,  # type: ignore[attr-defined]
                    "lang_name": widget.lang_name,  # type: ignore[attr-defined]
                }
            )
            subwidgets.append(widget_context)

        context["widget"]["subwidgets"] = subwidgets
        return context

    @staticmethod
    def build_widget_attrs(
        widget: forms.Widget,
        value: Any,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        """Build widget attributes, removing 'required' if not needed.

        Args:
            widget: The widget.
            value: Current value.
            attrs: Current attributes.

        Returns:
            Updated attributes.
        """
        attrs_copy: dict[str, Any] = dict(attrs)

        if (
            not widget.use_required_attribute(value) or not widget.is_required
        ) and "required" in attrs_copy:
            del attrs_copy["required"]

        return attrs_copy


class LocalizedCharFieldWidget(LocalizedFieldWidget):
    """Widget for LocalizedCharField with text inputs."""

    widget = forms.TextInput  # type: ignore[assignment]


class LocalizedFileWidget(LocalizedFieldWidget):
    """Widget for LocalizedFileField with file inputs."""

    widget = forms.ClearableFileInput  # type: ignore[assignment]


class AdminLocalizedFieldWidget(LocalizedFieldWidget):
    """Admin widget for localized fields with tab/dropdown support."""

    widget = widgets.AdminTextareaWidget

    def __init__(
        self,
        *args: Any,
        display_mode: str | None = None,
        **kwargs: Any,
    ):
        """Initialize the admin widget.

        Args:
            display_mode: "tab" or "dropdown". Uses settings if None.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.display_mode = display_mode or i18n_fields_settings.DISPLAY

    @property
    def template_name(self) -> str:  # type: ignore[override]
        """Get template name based on display mode."""
        if self.display_mode == "dropdown":
            return "i18n_fields/admin/widget_dropdown.html"
        return "i18n_fields/admin/widget_tabs.html"


class AdminLocalizedBooleanFieldWidget(AdminLocalizedFieldWidget):
    """Admin widget for LocalizedBooleanField with select dropdowns."""

    widget = forms.NullBooleanSelect  # type: ignore[assignment]

    def __init__(
        self,
        *args: Any,
        display_mode: str | None = None,
        **kwargs: Any,
    ):
        """Initialize with boolean choices."""
        # Pop display_mode before calling super since parent handles it
        super().__init__(*args, display_mode=display_mode, **kwargs)


class AdminLocalizedCharFieldWidget(AdminLocalizedFieldWidget):
    """Admin widget for LocalizedCharField."""

    widget = widgets.AdminTextInputWidget  # type: ignore[assignment]


class AdminLocalizedFileFieldWidget(AdminLocalizedFieldWidget):
    """Admin widget for LocalizedFileField."""

    widget = widgets.AdminFileWidget  # type: ignore[assignment]


class AdminLocalizedIntegerFieldWidget(AdminLocalizedFieldWidget):
    """Admin widget for LocalizedIntegerField."""

    widget = widgets.AdminIntegerFieldWidget  # type: ignore[assignment]


class AdminLocalizedFloatFieldWidget(AdminLocalizedFieldWidget):
    """Admin widget for LocalizedFloatField."""

    widget = forms.NumberInput  # type: ignore[assignment]
