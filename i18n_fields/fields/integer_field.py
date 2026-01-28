"""LocalizedIntegerField for integer values in multiple languages."""

from typing import TYPE_CHECKING, Any, cast

from django.conf import settings
from django.db.models.fields.json import KeyTransform
from django.db.utils import IntegrityError

from ..value import LocalizedIntegerValue, LocalizedValue
from .field import LocalizedField

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.models.sql.compiler import (
        SQLCompiler,
        _AsSqlType,  # pyright: ignore[reportPrivateUsage]
    )


class LocalizedIntegerFieldKeyTransform(KeyTransform):
    """Transform that casts JSON value to integer for proper sorting."""

    def as_sql(
        self,
        compiler: "SQLCompiler",
        connection: "BaseDatabaseWrapper",
        function: str | None = None,
        template: str | None = None,
        arg_joiner: str | None = None,
        **extra_context: Any,
    ) -> "_AsSqlType":
        """Generate SQL with integer cast.

        Args:
            compiler: The SQL compiler.
            connection: The database connection.
            function: Optional function name.
            template: Optional template string.
            arg_joiner: Optional argument joiner.
            **extra_context: Additional context arguments.

        Returns:
            Tuple of (sql, params).
        """
        sql, params = super().as_sql(
            compiler, connection, function, template, arg_joiner, **extra_context
        )
        return f"CAST({sql} AS INTEGER)", params


class LocalizedIntegerField(LocalizedField[LocalizedIntegerValue]):
    """Localized field for integer values.

    JSONField stores native integers, so no string conversion needed.

    Example:
        class Product(models.Model):
            stock = LocalizedIntegerField(blank=True, null=True)
    """

    attr_class: type[LocalizedIntegerValue] = LocalizedIntegerValue

    def get_transform(self, lookup_name: str) -> Any:
        """Get transform for selecting specific language with integer cast.

        Args:
            lookup_name: The language code.

        Returns:
            Transform function.
        """

        def _transform(*args: Any, **kwargs: Any) -> LocalizedIntegerFieldKeyTransform:
            return LocalizedIntegerFieldKeyTransform(lookup_name, *args, **kwargs)

        return _transform

    def from_db_value(  # type: ignore[override]
        self,
        value: dict[str, Any] | str | int | None,
        expression: Any,
        connection: Any,
    ) -> LocalizedIntegerValue | int | None:
        """Convert database value to LocalizedIntegerValue.

        Args:
            value: The database value.
            expression: The expression being evaluated.
            connection: The database connection.

        Returns:
            LocalizedIntegerValue or int for expressions.
        """
        db_value = super().from_db_value(value, expression, connection)  # type: ignore[arg-type]
        if db_value is None:
            return None

        # Handle individual key selection (returns string/int)
        if isinstance(db_value, str):
            try:
                return int(db_value)
            except ValueError:
                return None

        if isinstance(db_value, int | float):
            return int(db_value)

        if not isinstance(db_value, LocalizedValue):
            return db_value  # type: ignore[return-value]

        return self._convert_localized_value(db_value)

    def to_python(  # type: ignore[override]
        self, value: dict[str, Any] | int | None
    ) -> LocalizedIntegerValue:
        """Convert value to LocalizedIntegerValue.

        Args:
            value: The value to convert.

        Returns:
            LocalizedIntegerValue instance.
        """
        db_value = super().to_python(value)  # type: ignore[arg-type]
        return self._convert_localized_value(db_value)

    def get_prep_value(  # type: ignore[override]
        self, value: LocalizedIntegerValue | None
    ) -> dict[str, Any] | None:
        """Prepare value for database storage.

        Args:
            value: The value to prepare.

        Returns:
            Dictionary with integer values ready for JSON storage.
        """
        # Apply default values
        if self.default is not None:
            default_values = LocalizedIntegerValue(self.default)
            if isinstance(value, LocalizedIntegerValue):
                for lang_code, _ in settings.LANGUAGES:
                    local_value = value.get(lang_code)
                    if local_value is None:
                        value.set(lang_code, default_values.get(lang_code))

        prepped_value = super().get_prep_value(value)
        if prepped_value is None:
            return None

        # For lookups (e.g., stock__en=5), return scalar values as-is
        if not isinstance(prepped_value, dict):
            return None

        # Validate and ensure integer values
        for lang_code, _ in settings.LANGUAGES:
            local_value = prepped_value.get(lang_code)
            if local_value is not None:
                try:
                    prepped_value[lang_code] = int(local_value)
                except (TypeError, ValueError) as err:
                    raise IntegrityError(
                        f'non-integer value in column "{self.name}.{lang_code}" '
                        "violates integer constraint"
                    ) from err

        return prepped_value

    def formfield(self, **kwargs: Any) -> Any:  # type: ignore[override]
        """Get the form field for this field.

        Args:
            **kwargs: Keyword arguments for the form field.

        Returns:
            The form field instance.
        """
        from ..forms import LocalizedIntegerFieldForm

        defaults = {"form_class": LocalizedIntegerFieldForm}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    @staticmethod
    def _convert_localized_value(value: LocalizedValue) -> LocalizedIntegerValue:
        """Convert LocalizedValue to LocalizedIntegerValue.

        Args:
            value: The value to convert.

        Returns:
            LocalizedIntegerValue instance.
        """
        integer_values: dict[str, int | None] = {}
        for lang_code, _ in settings.LANGUAGES:
            local_value = value.get(lang_code)

            if local_value is None:
                integer_values[lang_code] = None
            elif isinstance(local_value, str) and local_value.strip() == "":
                integer_values[lang_code] = None
            else:
                try:
                    integer_values[lang_code] = int(local_value)
                except (ValueError, TypeError):
                    integer_values[lang_code] = None

        return LocalizedIntegerValue(cast(dict[str, Any], integer_values))
