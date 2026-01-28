"""LocalizedFloatField for float values in multiple languages."""

from typing import Any, cast

from django.conf import settings
from django.db.utils import IntegrityError

from ..value import LocalizedFloatValue, LocalizedValue
from .field import LocalizedField


class LocalizedFloatField(LocalizedField[LocalizedFloatValue]):
    """Localized field for float values.

    JSONField stores native floats, so no string conversion needed.

    Example:
        class Product(models.Model):
            price = LocalizedFloatField(blank=True, null=True)
    """

    attr_class: type[LocalizedFloatValue] = LocalizedFloatValue

    def from_db_value(  # type: ignore[override]
        self,
        value: dict[str, Any] | str | float | int | None,
        expression: Any,
        connection: Any,
    ) -> LocalizedFloatValue | float | None:
        """Convert database value to LocalizedFloatValue.

        Args:
            value: The database value.
            expression: The expression being evaluated.
            connection: The database connection.

        Returns:
            LocalizedFloatValue or float for expressions.
        """
        db_value = super().from_db_value(value, expression, connection)  # type: ignore[arg-type]
        if db_value is None:
            return None

        # Handle individual key selection
        if isinstance(db_value, str):
            try:
                return float(db_value)
            except ValueError:
                return None

        if isinstance(db_value, int | float):
            return float(db_value)

        if not isinstance(db_value, LocalizedValue):
            return db_value  # type: ignore[return-value]

        return self._convert_localized_value(db_value)

    def to_python(  # type: ignore[override]
        self, value: dict[str, Any] | float | int | None
    ) -> LocalizedFloatValue:
        """Convert value to LocalizedFloatValue.

        Args:
            value: The value to convert.

        Returns:
            LocalizedFloatValue instance.
        """
        db_value = super().to_python(value)  # type: ignore[arg-type]
        return self._convert_localized_value(db_value)

    def get_prep_value(  # type: ignore[override]
        self, value: LocalizedFloatValue | None
    ) -> dict[str, Any] | None:
        """Prepare value for database storage.

        Args:
            value: The value to prepare.

        Returns:
            Dictionary with float values ready for JSON storage.
        """
        # Apply default values
        if self.default is not None:
            default_values = LocalizedFloatValue(self.default)
            if isinstance(value, LocalizedFloatValue):
                for lang_code, _ in settings.LANGUAGES:
                    local_value = value.get(lang_code)
                    if local_value is None:
                        value.set(lang_code, default_values.get(lang_code))

        prepped_value = super().get_prep_value(value)
        if prepped_value is None:
            return None

        if not isinstance(prepped_value, dict):
            return None

        # Validate and ensure float values
        for lang_code, _ in settings.LANGUAGES:
            local_value = prepped_value.get(lang_code)
            if local_value is not None:
                try:
                    prepped_value[lang_code] = float(local_value)
                except (TypeError, ValueError) as err:
                    raise IntegrityError(
                        f'non-float value in column "{self.name}.{lang_code}" '
                        "violates float constraint"
                    ) from err

        return prepped_value

    def formfield(self, **kwargs: Any) -> Any:  # type: ignore[override]
        """Get the form field for this field.

        Args:
            **kwargs: Keyword arguments for the form field.

        Returns:
            The form field instance.
        """
        from ..forms import LocalizedFloatFieldForm

        defaults = {"form_class": LocalizedFloatFieldForm}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    @staticmethod
    def _convert_localized_value(value: LocalizedValue) -> LocalizedFloatValue:
        """Convert LocalizedValue to LocalizedFloatValue.

        Args:
            value: The value to convert.

        Returns:
            LocalizedFloatValue instance.
        """
        float_values: dict[str, float | None] = {}
        for lang_code, _ in settings.LANGUAGES:
            local_value = value.get(lang_code)

            if local_value is None:
                float_values[lang_code] = None
            elif isinstance(local_value, str) and local_value.strip() == "":
                float_values[lang_code] = None
            else:
                try:
                    float_values[lang_code] = float(local_value)
                except (ValueError, TypeError):
                    float_values[lang_code] = None

        return LocalizedFloatValue(cast(dict[str, Any], float_values))
