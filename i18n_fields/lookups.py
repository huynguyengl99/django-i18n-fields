"""Query lookups for localized fields using JSONField."""

from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db.models import TextField, Transform
from django.db.models.expressions import Col
from django.db.models.fields.json import KeyTextTransform, KeyTransform
from django.db.models.functions import Coalesce, NullIf
from django.db.models.lookups import (
    Contains,
    EndsWith,
    Exact,
    IContains,
    IEndsWith,
    IExact,
    In,
    IRegex,
    IsNull,
    IStartsWith,
    Regex,
    StartsWith,
)
from django.db.models.sql.compiler import SQLCompiler
from django.utils import translation

from .settings import i18n_fields_settings

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper


class LocalizedLookupMixin:
    """Mixin that transforms lookups to operate on the current language key.

    When filtering on a LocalizedField without specifying a language,
    this mixin automatically selects the current language's value.

    Example:
        # Without this mixin: Article.objects.filter(title={'en': 'Hello'})
        # With this mixin: Article.objects.filter(title='Hello')  # Uses current language
    """

    lhs: Any
    rhs: Any

    def process_lhs(
        self,
        compiler: SQLCompiler,
        connection: "BaseDatabaseWrapper",
        lhs: Any | None = None,
    ) -> tuple[str, list[Any]]:
        """Process left-hand side of lookup to select current language key.

        Args:
            compiler: SQL compiler.
            connection: Database connection.
            lhs: Left-hand side expression (unused).

        Returns:
            Tuple of (sql, params).
        """
        # If LHS is already a KeyTransform, it's already selecting a specific language
        if isinstance(self.lhs, KeyTransform | KeyTextTransform):
            return super().process_lhs(compiler, connection, lhs)  # type: ignore[misc, no-any-return]

        # If this is a custom expression, don't modify it
        if not isinstance(self.lhs, Col):
            return super().process_lhs(compiler, connection, lhs)  # type: ignore[misc, no-any-return]

        # Select the key for the current language using KeyTextTransform
        # to get the actual text value, not the JSON-encoded value
        language = translation.get_language() or settings.LANGUAGE_CODE
        self.lhs = KeyTextTransform(language, self.lhs)

        return super().process_lhs(compiler, connection, lhs)  # type: ignore[misc, no-any-return]

    def get_prep_lookup(self) -> Any:
        """Prepare the right-hand side value for the lookup.

        Returns:
            Prepared lookup value.
        """
        # Don't convert booleans to strings for isnull lookups
        if isinstance(self.rhs, bool):
            return self.rhs
        return self.rhs


class LocalizedExact(LocalizedLookupMixin, Exact):  # type: ignore[type-arg]
    """Exact match lookup for localized fields."""

    pass


class LocalizedIExact(LocalizedLookupMixin, IExact):  # type: ignore[type-arg]
    """Case-insensitive exact match lookup for localized fields."""

    pass


class LocalizedIn(LocalizedLookupMixin, In):  # type: ignore[type-arg]
    """In list lookup for localized fields."""

    pass


class LocalizedContains(LocalizedLookupMixin, Contains):
    """Contains lookup for localized fields."""

    pass


class LocalizedIContains(LocalizedLookupMixin, IContains):
    """Case-insensitive contains lookup for localized fields."""

    pass


class LocalizedStartsWith(LocalizedLookupMixin, StartsWith):
    """Starts with lookup for localized fields."""

    pass


class LocalizedIStartsWith(LocalizedLookupMixin, IStartsWith):
    """Case-insensitive starts with lookup for localized fields."""

    pass


class LocalizedEndsWith(LocalizedLookupMixin, EndsWith):
    """Ends with lookup for localized fields."""

    pass


class LocalizedIEndsWith(LocalizedLookupMixin, IEndsWith):
    """Case-insensitive ends with lookup for localized fields."""

    pass


class LocalizedIsNull(LocalizedLookupMixin, IsNull):
    """Is null lookup for localized fields."""

    pass


class LocalizedRegex(LocalizedLookupMixin, Regex):
    """Regex lookup for localized fields."""

    pass


class LocalizedIRegex(LocalizedLookupMixin, IRegex):
    """Case-insensitive regex lookup for localized fields."""

    pass


class ActiveRefLookup(KeyTextTransform):
    """Transform that selects the value in the current active language.

    Usage:
        Article.objects.values('title__active_ref')
    """

    lookup_name = "active_ref"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize with the current language key."""
        # Get the current language before calling super().__init__
        language = translation.get_language() or settings.LANGUAGE_CODE
        # Initialize KeyTextTransform with the language key
        super().__init__(language, *args, **kwargs)


class TranslatedRefLookup(Transform):
    """Transform that selects the value with fallback to other languages.

    Uses the FALLBACKS setting to determine fallback order.

    Usage:
        Article.objects.values('title__translated_ref')
    """

    lookup_name = "translated_ref"

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Create the appropriate expression based on language fallbacks."""
        # Extract lhs from args
        lhs = args[0] if args else kwargs.get("lhs")

        language = translation.get_language()
        fallbacks = i18n_fields_settings.FALLBACKS
        target_languages = list(fallbacks.get(language, []))

        if not target_languages and language != settings.LANGUAGE_CODE:
            target_languages.append(settings.LANGUAGE_CODE)

        if language:
            target_languages.insert(0, language)

        # Ensure we have at least one language
        if not target_languages:
            target_languages = [settings.LANGUAGE_CODE]

        # If only one language, return KeyTextTransform directly
        if len(target_languages) == 1:
            return KeyTextTransform(target_languages[0], lhs)

        # Multiple languages - use Coalesce for fallback
        from django.db.models import Value

        return Coalesce(
            *[
                NullIf(
                    KeyTextTransform(lang, lhs),
                    Value(""),
                    output_field=TextField(),
                )
                for lang in target_languages
            ]
        )


def register_lookups(field_class: type) -> None:
    """Register all localized lookups on the given field class.

    Args:
        field_class: The field class to register lookups on.
    """
    lookups = [
        LocalizedExact,
        LocalizedIExact,
        LocalizedIn,
        LocalizedContains,
        LocalizedIContains,
        LocalizedStartsWith,
        LocalizedIStartsWith,
        LocalizedEndsWith,
        LocalizedIEndsWith,
        LocalizedIsNull,
        LocalizedRegex,
        LocalizedIRegex,
        ActiveRefLookup,
        TranslatedRefLookup,
    ]

    for lookup in lookups:
        field_class.register_lookup(lookup)  # type: ignore[attr-defined]
