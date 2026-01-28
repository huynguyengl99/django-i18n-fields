"""LocalizedBooleanField for boolean values in multiple languages."""

from typing import Any, cast

from django.conf import settings
from django.db.utils import IntegrityError

from ..value import LocalizedBooleanValue, LocalizedValue
from .field import LocalizedField


class LocalizedBooleanField(LocalizedField[LocalizedBooleanValue]):
    """Localized field for boolean values.

    JSONField stores native booleans, so no string conversion needed.

    Example:
        class Article(models.Model):
            is_featured = LocalizedBooleanField(blank=True, null=True)
    """

    attr_class: type[LocalizedBooleanValue] = LocalizedBooleanValue

    def from_db_value(  # type: ignore[override]
        self,
        value: dict[str, Any] | str | bool | None,
        expression: Any,
        connection: Any,
    ) -> LocalizedBooleanValue | bool | None:
        """Convert database value to LocalizedBooleanValue.

        Args:
            value: The database value.
            expression: The expression being evaluated.
            connection: The database connection.

        Returns:
            LocalizedBooleanValue or bool for expressions.
        """
        db_value = super().from_db_value(value, expression, connection)
        if db_value is None:
            return None

        # Handle individual key selection
        if isinstance(db_value, str):
            return db_value.lower() == "true"

        if isinstance(db_value, bool):
            return db_value

        if not isinstance(db_value, LocalizedValue):
            return db_value  # type: ignore[return-value]

        return self._convert_localized_value(db_value)

    def to_python(self, value: dict[str, Any] | str | None) -> LocalizedBooleanValue:
        """Convert value to LocalizedBooleanValue.

        Args:
            value: The value to convert.

        Returns:
            LocalizedBooleanValue instance.
        """
        db_value = super().to_python(value)
        return self._convert_localized_value(db_value)

    def get_prep_value(  # type: ignore[override]
        self, value: LocalizedBooleanValue | None
    ) -> dict[str, Any] | None:
        """Prepare value for database storage.

        Args:
            value: The value to prepare.

        Returns:
            Dictionary with boolean values ready for JSON storage.
        """
        # Apply default values
        if self.default is not None:
            default_values = LocalizedBooleanValue(self.default)
            if isinstance(value, LocalizedBooleanValue):
                for lang_code, _ in settings.LANGUAGES:
                    local_value = value.get(lang_code)
                    if local_value is None:
                        value.set(lang_code, default_values.get(lang_code))

        prepped_value = super().get_prep_value(value)
        if prepped_value is None:
            return None

        # If parent returned a scalar (for lookups like is_featured__en=True), return it as-is
        if isinstance(prepped_value, str | int | float | bool):
            return prepped_value  # type: ignore[return-value]

        # Validate and ensure boolean values
        for lang_code, _ in settings.LANGUAGES:
            local_value = prepped_value.get(lang_code)
            if local_value is not None:
                if isinstance(local_value, bool):
                    continue
                if isinstance(local_value, str):
                    if local_value.lower() in ("true", "false"):
                        prepped_value[lang_code] = local_value.lower() == "true"
                        continue
                raise IntegrityError(
                    f'non-boolean value in column "{self.name}.{lang_code}" '
                    "violates boolean constraint"
                )

        return prepped_value

    def formfield(self, **kwargs: Any) -> Any:  # type: ignore[override]
        """Get the form field for this field.

        Args:
            **kwargs: Keyword arguments for the form field.

        Returns:
            The form field instance.
        """
        from ..forms import LocalizedBooleanFieldForm

        defaults = {"form_class": LocalizedBooleanFieldForm}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    @staticmethod
    def _convert_localized_value(value: LocalizedValue) -> LocalizedBooleanValue:
        """Convert LocalizedValue to LocalizedBooleanValue.

        Args:
            value: The value to convert.

        Returns:
            LocalizedBooleanValue instance.
        """
        boolean_values: dict[str, bool | None] = {}
        for lang_code, _ in settings.LANGUAGES:
            local_value = value.get(lang_code)

            if local_value is None:
                boolean_values[lang_code] = None
            elif isinstance(local_value, bool):
                boolean_values[lang_code] = local_value
            elif isinstance(local_value, str):
                if local_value.lower() == "true":
                    boolean_values[lang_code] = True
                elif local_value.lower() == "false":
                    boolean_values[lang_code] = False
                else:
                    boolean_values[lang_code] = None
            else:
                boolean_values[lang_code] = None

        return LocalizedBooleanValue(cast(dict[str, Any], boolean_values))
