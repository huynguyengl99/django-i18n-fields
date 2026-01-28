"""LocalizedValue classes for storing multilingual field values."""

from collections.abc import Callable, Iterable
from typing import Any, cast

from django.conf import settings
from django.utils import translation

from .settings import i18n_fields_settings


class LocalizedValue(dict[str, Any]):
    """Represents the value of a LocalizedField as a dict-like object."""

    default_value: Any = None

    def __init__(
        self, keys: dict[str, Any] | str | list[Any] | Callable[[], Any] | None = None
    ):
        """Initialize a new LocalizedValue instance.

        Args:
            keys: Dictionary of language codes to values, or other value types.
        """
        super().__init__({})
        self._interpret_value(keys)

    def get(self, language: str | None = None, default: Any = None) -> Any:
        """Get the value in the specified or primary language.

        Args:
            language: The language code. Defaults to LANGUAGE_CODE.
            default: Default value if not found.

        Returns:
            The value in the specified language.
        """
        lang_key = language or settings.LANGUAGE_CODE
        value: Any = super().get(lang_key, default)
        return value if value is not None else default

    def set(self, language: str, value: Any) -> "LocalizedValue":
        """Set the value for a specific language.

        Args:
            language: The language code.
            value: The value to set.

        Returns:
            Self for chaining.
        """
        self[language] = value
        self.__dict__.update(self)
        return self

    def deconstruct(self) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
        """Deconstruct this value for migrations.

        Returns:
            Tuple of (path, args, kwargs) for reconstruction.
        """
        path = f"i18n_fields.value.{self.__class__.__name__}"
        return path, [dict(self)], {}

    def _interpret_value(self, value: Any) -> None:
        """Interpret and set value from various input types.

        Args:
            value: The value to interpret.
        """
        for lang_code, _ in settings.LANGUAGES:
            self.set(lang_code, self.default_value)

        if callable(value):
            value = value()

        if isinstance(value, str):
            self.set(settings.LANGUAGE_CODE, value)

        elif isinstance(value, dict):
            value_dict = cast(dict[str, Any], value)
            for lang_code, _ in settings.LANGUAGES:
                lang_value: Any = value_dict.get(lang_code, self.default_value)
                self.set(lang_code, lang_value)

        elif isinstance(value, Iterable) and not isinstance(value, str | bytes):
            for val in value:  # pyright: ignore[reportUnknownVariableType]
                self._interpret_value(val)

    def translate(self, language: str | None = None) -> Any:
        """Get the value in the specified or active language with fallback.

        Args:
            language: The language to get value for. Uses active language if None.

        Returns:
            The value in the target language or fallback.
        """
        target_language = (
            language or translation.get_language() or settings.LANGUAGE_CODE
        )

        fallbacks = i18n_fields_settings.FALLBACKS
        target_languages = fallbacks.get(target_language, [settings.LANGUAGE_CODE])

        for lang_code in [target_language] + target_languages:
            value = self.get(lang_code)
            # Check for not None and not default_value to support False, 0, but skip empty fallbacks
            if value is not None and value != self.default_value:
                return value

        return None

    def is_empty(self) -> bool:
        """Check if all languages contain the default value."""
        for lang_code, _ in settings.LANGUAGES:
            if self.get(lang_code) != self.default_value:
                return False
        return True

    def __str__(self) -> str:
        """Get the value in the current language with fallback."""
        return self.translate() or ""

    def __eq__(self, other: object) -> bool:
        """Compare for equality."""
        if not isinstance(other, type(self)):
            if isinstance(other, str):
                return self.__str__() == other
            return False

        for lang_code, _ in settings.LANGUAGES:
            if self.get(lang_code) != other.get(lang_code):
                return False
        return True

    def __ne__(self, other: object) -> bool:
        """Compare for inequality."""
        return not self.__eq__(other)

    def __setattr__(self, language: str, value: Any) -> None:
        """Set value for a language via attribute access."""
        self.set(language, value)

    def __repr__(self) -> str:
        """Get string representation."""
        return f"{self.__class__.__name__}<{self.__dict__}> 0x{id(self)}"


class LocalizedStringValue(LocalizedValue):
    """LocalizedValue with empty string as default."""

    default_value = ""


class LocalizedFileValue(LocalizedValue):
    """LocalizedValue for file fields."""

    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to the current language's file."""
        value = self.get(translation.get_language())
        if hasattr(value, name):
            return getattr(value, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __str__(self) -> str:
        """Return string representation."""
        return str(super().__str__())


class LocalizedBooleanValue(LocalizedValue):
    """LocalizedValue for boolean fields."""

    default_value = None

    def translate(self, language: str | None = None) -> bool | None:
        """Get the boolean value in the current language."""
        value = super().translate(language)
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            if value.strip() == "":
                return None
            return value.lower() == "true"

        return bool(value)

    def __bool__(self) -> bool:
        """Get boolean value."""
        value = self.translate()
        return bool(value) if value is not None else False

    def __str__(self) -> str:
        """Return string representation."""
        value = self.translate()
        return str(value) if value is not None else ""


class LocalizedNumericValue(LocalizedValue):
    """Base class for numeric localized values."""

    default_value = None

    def __int__(self) -> int:
        """Get integer value."""
        value = self.translate()
        if value is None:
            return 0
        return int(value)

    def __float__(self) -> float:
        """Get float value."""
        value = self.translate()
        if value is None:
            return 0.0
        return float(value)

    def __str__(self) -> str:
        """Return string representation."""
        value = self.translate()
        return str(value) if value is not None else ""


class LocalizedIntegerValue(LocalizedNumericValue):
    """LocalizedValue for integer fields."""

    def translate(self, language: str | None = None) -> int | None:
        """Get the integer value in the current language."""
        value = LocalizedValue.translate(self, language)
        if value is None:
            return None

        if isinstance(value, int):
            return value

        if isinstance(value, str):
            if value.strip() == "":
                return None
            try:
                return int(value)
            except ValueError:
                return None

        try:
            return int(value)
        except (ValueError, TypeError):
            return None


class LocalizedFloatValue(LocalizedNumericValue):
    """LocalizedValue for float fields."""

    def translate(self, language: str | None = None) -> float | None:
        """Get the float value in the current language."""
        value = LocalizedValue.translate(self, language)
        if value is None:
            return None

        if isinstance(value, int | float):
            return float(value)

        if isinstance(value, str):
            if value.strip() == "":
                return None
            try:
                return float(value)
            except ValueError:
                return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None
