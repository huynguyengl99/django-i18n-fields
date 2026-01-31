"""Admin mixins and utilities for localized fields."""

from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING, Any, ClassVar, Generic, cast

from django.contrib import admin
from django.db import models
from django.db.models import Model

from typing_extensions import TypeVar

from . import widgets
from .fields import (
    LocalizedBooleanField,
    LocalizedCharField,
    LocalizedField,
    LocalizedFileField,
    LocalizedFloatField,
    LocalizedIntegerField,
    LocalizedTextField,
)
from .value import LocalizedValue

if TYPE_CHECKING:
    from django.contrib.admin.options import (
        _FieldOpts,
        _FieldsetSpec,
        _ListDisplayT,
    )  # noqa
    from django.utils.datastructures import _ListOrTuple  # noqa
    from django.utils.functional import _StrOrPromise  # noqa


_ModelT = TypeVar("_ModelT", bound=Model, default=Model)


# Order matters! More specific classes must come before their base classes
# because isinstance() matches subclasses
# Inheritance: LocalizedTextField -> LocalizedCharField -> LocalizedField
FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS: dict[type, type] = {
    # Most specific first
    LocalizedTextField: widgets.AdminLocalizedFieldWidget,  # Textarea
    LocalizedCharField: widgets.AdminLocalizedCharFieldWidget,  # TextInput
    LocalizedFileField: widgets.AdminLocalizedFileFieldWidget,
    LocalizedBooleanField: widgets.AdminLocalizedBooleanFieldWidget,
    LocalizedIntegerField: widgets.AdminLocalizedIntegerFieldWidget,
    LocalizedFloatField: widgets.AdminLocalizedFloatFieldWidget,
    # Base class must be last
    LocalizedField: widgets.AdminLocalizedFieldWidget,
}


def _get_localized_field_display(obj: models.Model, field_name: str) -> str:
    """Get the display value for a localized field (for list_display).

    This helper function is used to properly display LocalizedValue
    objects in list_display contexts - shows just the translated value.

    Args:
        obj: The model instance.
        field_name: The name of the localized field.

    Returns:
        The translated string value for display.
    """
    value = getattr(obj, field_name, None)
    if value is None:
        return "-"
    if isinstance(value, LocalizedValue):
        return str(value) or "-"
    if isinstance(value, dict):
        # If it's still a dict, try to get the translated value
        from django.conf import settings
        from django.utils import translation

        lang = translation.get_language() or settings.LANGUAGE_CODE
        dict_value = cast(dict[str, Any], value)
        return str(dict_value.get(lang, "")) or "-"
    return str(value)


def _get_localized_field_readonly_display(
    obj: models.Model, field_name: str, display_mode: str = "tab"
) -> str:
    """Get the readonly display HTML for a localized field.

    This helper function creates a tab/dropdown interface for readonly
    localized fields in admin change forms.

    Args:
        obj: The model instance.
        field_name: The name of the localized field.
        display_mode: "tab" or "dropdown".

    Returns:
        HTML string with the readonly tab/dropdown interface.
    """
    from django.conf import settings as django_settings
    from django.utils.html import escape
    from django.utils.safestring import mark_safe

    value = getattr(obj, field_name, None)

    # Convert to dict if needed
    if value is None:
        value_dict: dict[str, Any] = {}
    elif isinstance(value, LocalizedValue):
        value_dict = dict(value)
    elif isinstance(value, dict):
        value_dict = cast(dict[str, Any], value)
    else:
        value_dict = {django_settings.LANGUAGE_CODE: str(value)}

    # Get languages
    languages: list[tuple[str, str]] = list(django_settings.LANGUAGES)

    if display_mode == "dropdown":
        # Dropdown mode - show select and content
        options_html = ""
        contents_html = ""
        for i, (lang_code, lang_name) in enumerate(languages):
            lang_value = value_dict.get(lang_code, "") or ""
            selected = "selected" if i == 0 else ""
            options_html += f'<option value="{escape(lang_code)}" {selected}>{escape(lang_name)}</option>'
            display_style = "" if i == 0 else "display: none;"
            contents_html += f'<div class="i18n-readonly-content" data-lang="{escape(lang_code)}" style="{display_style}">{escape(str(lang_value))}</div>'

        return mark_safe(
            f'<div class="i18n-readonly-widget i18n-dropdown-mode">'
            f'<select class="i18n-readonly-select" onchange="i18nReadonlySwitch(this)">{options_html}</select>'
            f'<div class="i18n-readonly-contents">{contents_html}</div>'
            f"</div>"
        )
    else:
        # Tab mode - show tabs and content
        tabs_html = ""
        contents_html = ""
        for i, (lang_code, lang_name) in enumerate(languages):
            lang_value = value_dict.get(lang_code, "") or ""
            active_class = "active" if i == 0 else ""
            tabs_html += f'<button type="button" class="i18n-readonly-tab {active_class}" data-lang="{escape(lang_code)}" onclick="i18nReadonlyTabClick(this)">{escape(lang_name)}</button>'
            display_style = "" if i == 0 else "display: none;"
            contents_html += f'<div class="i18n-readonly-content {active_class}" data-lang="{escape(lang_code)}" style="{display_style}">{escape(str(lang_value))}</div>'

        return mark_safe(
            f'<div class="i18n-readonly-widget i18n-tab-mode">'
            f'<div class="i18n-readonly-tabs">{tabs_html}</div>'
            f'<div class="i18n-readonly-contents">{contents_html}</div>'
            f"</div>"
        )


class LocalizedFieldsAdminMixin(Generic[_ModelT]):
    """Mixin for Django Admin that enables localized field widgets.

    Add this mixin to your ModelAdmin to get fancy tab/dropdown widgets
    for all localized fields.

    Example:
        @admin.register(Article)
        class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
            pass

    You can override the display mode per-admin:
        @admin.register(Article)
        class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
            localized_fields_display = "dropdown"  # or "tab"
    """

    # Override to change display mode: "tab" or "dropdown"
    localized_fields_display: str | None = None
    list_display: "_ListDisplayT[_ModelT]"
    search_fields: ClassVar["_ListOrTuple[str]"]
    readonly_fields: ClassVar["_ListOrTuple[str]"]
    model: type[_ModelT]

    # Internal: mapping from original field name to readonly method name
    _localized_readonly_field_map: dict[str, str]

    class Media:
        css = {"all": ("i18n_fields/i18n-fields-admin.css",)}
        js = (
            "admin/js/jquery.init.js",
            "i18n_fields/i18n-fields-admin.js",
        )

    def __init__(self, model: Any, admin_site: Any) -> None:
        """Initialize the admin with dynamic display methods for localized fields."""
        # Initialize the field mapping
        self._localized_readonly_field_map = {}
        # Set up readonly display methods BEFORE super().__init__()
        # because Django may cache method lookups during initialization.
        # Note: self.model is not set yet, so we use the model argument directly.
        self._setup_readonly_methods_early(model)
        super().__init__(model, admin_site)  # type: ignore[call-arg]
        self._setup_localized_field_displays()

    def _setup_readonly_methods_early(self, model: Any) -> None:
        """Set up readonly field methods early, before parent init.

        This method creates custom display methods for localized fields
        and replaces field names in readonly_fields with method names.
        This is necessary because Django's lookup_field() finds model fields
        first and uses their string representation, bypassing admin methods
        with the same name.
        """
        if model is None:
            return
        if not hasattr(self, "readonly_fields") or not self.readonly_fields:
            return

        # Get localized field names from the model
        localized_field_names: set[str] = set()
        for field in model._meta.get_fields():
            if isinstance(field, LocalizedField):
                localized_field_names.add(field.name)

        if not localized_field_names:
            return

        display_mode = getattr(self, "localized_fields_display", None) or "tab"

        # Build new readonly_fields list, replacing localized field names
        # with custom method names
        new_readonly_fields: list[str] = []
        for item in self.readonly_fields:
            if item in localized_field_names:
                # Create a unique method name that won't conflict with model field
                method_name = f"_readonly_{item}_display"

                # Store the mapping for use in get_fieldsets
                self._localized_readonly_field_map[item] = method_name

                # Check if method already exists on the class
                if not hasattr(self.__class__, method_name):
                    # Create and set the method on the class
                    def make_method(field_name: str, mode: str) -> Any:
                        def method(admin_self: Any, obj: models.Model) -> str:
                            return _get_localized_field_readonly_display(
                                obj, field_name, mode
                            )

                        method.short_description = field_name.replace("_", " ").title()  # type: ignore[attr-defined]
                        return method

                    setattr(
                        self.__class__, method_name, make_method(item, display_mode)
                    )

                new_readonly_fields.append(method_name)
            else:
                new_readonly_fields.append(item)

        # Replace readonly_fields with the new list
        self.readonly_fields = new_readonly_fields  # type: ignore

    def get_fieldsets(self, request: Any, obj: Any = None) -> "_FieldsetSpec":
        """Get fieldsets with localized readonly field names replaced.

        This overrides the parent method to replace original field names
        with their readonly method names in fieldsets.
        """
        fieldsets = cast("_FieldsetSpec", super().get_fieldsets(request, obj))  # type: ignore[misc]

        if not self._localized_readonly_field_map:
            return fieldsets

        # Replace field names in fieldsets
        new_fieldsets: list[tuple[_StrOrPromise | None, _FieldOpts]] = []
        for fieldset_item in fieldsets:
            name = fieldset_item[0]
            options = fieldset_item[1]
            new_options = options.copy()
            if "fields" in new_options:
                new_fields: list[Any] = []
                for field in new_options["fields"]:
                    if isinstance(field, list | tuple):
                        # Handle inline fields (multiple fields on same line)
                        new_inline: list[str] = []
                        for f in field:
                            new_inline.append(
                                self._localized_readonly_field_map.get(f, f)
                            )
                        new_fields.append(
                            type(field)(
                                new_inline  # pyright: ignore[reportArgumentType]
                            )
                        )
                    else:
                        new_fields.append(
                            self._localized_readonly_field_map.get(field, field)
                        )
                new_options["fields"] = new_fields
            new_fieldsets.append((name, new_options))

        return new_fieldsets

    def _setup_localized_field_displays(self) -> None:
        """Set up display methods for localized fields in list_display."""
        if (
            not hasattr(self, "model")
            or self.model is None  # pyright: ignore[reportUnnecessaryComparison]
        ):
            return

        # Get all localized fields from the model
        localized_field_names: set[str] = set()
        for (
            field  # pyright: ignore[reportUnknownVariableType]
        ) in (
            self.model._meta.get_fields()  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        ):
            if isinstance(field, LocalizedField):
                localized_field_names.add(field.name)

        # Replace field names in list_display with display methods
        if hasattr(self, "list_display") and self.list_display:
            new_list_display: list[str | Callable[[Any], str | bool]] = []
            for item in self.list_display:
                if item in localized_field_names:
                    # Create a display method for this field
                    method_name = f"_localized_{item}_display"
                    if not hasattr(self, method_name):
                        # Create the method dynamically
                        display_func = partial(
                            _get_localized_field_display, field_name=item  # type: ignore[arg-type]
                        )
                        display_func.short_description = item.replace("_", " ").title()  # type: ignore[attr-defined, union-attr]
                        display_func.admin_order_field = item  # type: ignore[attr-defined]
                        setattr(self, method_name, display_func)
                    new_list_display.append(method_name)
                else:
                    new_list_display.append(item)
            self.list_display = new_list_display

        # Note: readonly fields are handled in _setup_readonly_methods_early()

    def formfield_for_dbfield(
        self,
        db_field: "models.Field[Any, Any]",
        request: Any,
        **kwargs: Any,
    ) -> Any:
        """Override to use localized field widgets with display mode.

        Args:
            db_field: The database field.
            request: The HTTP request.
            **kwargs: Additional keyword arguments.

        Returns:
            The form field for this database field.
        """
        # Check if this is a localized field type
        for (
            field_class,
            widget_class,
        ) in FORMFIELD_FOR_LOCALIZED_FIELDS_DEFAULTS.items():
            if isinstance(db_field, field_class):
                # Instantiate widget with display_mode if set
                if self.localized_fields_display:
                    kwargs["widget"] = widget_class(
                        display_mode=self.localized_fields_display
                    )
                else:
                    kwargs["widget"] = widget_class()
                break

        return super().formfield_for_dbfield(db_field, request, **kwargs)  # type: ignore[misc]

    def get_search_results(
        self, request: Any, queryset: Any, search_term: str
    ) -> tuple[Any, bool]:
        """Override search to handle localized fields.

        This method extends Django's default search to properly search within
        JSONB fields for localized content.

        Args:
            request: The HTTP request.
            queryset: The base queryset.
            search_term: The search term from the user.

        Returns:
            Tuple of (filtered_queryset, use_distinct).
        """
        if not search_term or not hasattr(self, "search_fields"):
            return super().get_search_results(request, queryset, search_term)  # type: ignore[misc,no-any-return]

        # Get localized field names
        localized_field_names: set[str] = set()
        for field in self.model._meta.get_fields():
            if isinstance(field, LocalizedField):
                localized_field_names.add(field.name)

        # Separate localized and non-localized search fields
        localized_search_fields: list[str] = []
        non_localized_search_fields: list[str] = []

        for search_field in self.search_fields:
            # Remove any search field prefixes (^, =, @)
            field_name: str = search_field.lstrip("^=@")
            if field_name in localized_field_names:
                localized_search_fields.append(search_field)
            else:
                non_localized_search_fields.append(search_field)

        # Handle non-localized fields with default search
        use_distinct: bool
        if non_localized_search_fields:
            # Temporarily set search_fields to only non-localized ones
            original_search_fields = self.search_fields
            self.search_fields = non_localized_search_fields  # type: ignore[misc]
            queryset, use_distinct = super().get_search_results(request, queryset, search_term)  # type: ignore[misc]
            self.search_fields = original_search_fields  # type: ignore[misc]
        else:
            use_distinct = False

        # Handle localized fields with JSONB search
        if localized_search_fields:
            from django.conf import settings
            from django.db.models import Q

            # Build Q objects for each localized field and language
            q_list: list[Q] = []
            for search_field in localized_search_fields:
                # Remove any prefix
                field_name_stripped: str = search_field.lstrip("^=@")

                # Build Q objects for each language
                for lang_code, _ in settings.LANGUAGES:
                    # Use the registered lookup for searching
                    lookup = f"{field_name_stripped}__{lang_code}__icontains"
                    q_list.append(Q(**{lookup: search_term}))

            # Combine all Q objects with OR
            if q_list:
                import operator
                from functools import reduce

                search_q = reduce(operator.or_, q_list)
                queryset = queryset.filter(  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
                    search_q
                )
                use_distinct = True

        return queryset, use_distinct  # pyright: ignore[reportUnknownVariableType]


if TYPE_CHECKING:

    class BaseLocalizedFieldsAdmin(
        LocalizedFieldsAdminMixin[_ModelT], admin.ModelAdmin[_ModelT], Generic[_ModelT]
    ):
        pass

else:

    class BaseLocalizedFieldsAdmin(
        LocalizedFieldsAdminMixin, admin.ModelAdmin, Generic[_ModelT]
    ):
        pass


class LocalizedFieldsAdmin(BaseLocalizedFieldsAdmin[_ModelT], Generic[_ModelT]):
    pass
