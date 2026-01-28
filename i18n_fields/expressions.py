"""Query expressions for localized fields."""

from django.conf import settings
from django.db.models import F
from django.db.models.fields.json import KeyTextTransform
from django.utils import translation


class LocalizedRef(KeyTextTransform):
    """Expression that selects the value in a specific language from a localized field.

    This can be used in annotations, values(), order_by(), and other QuerySet methods.

    Example:
        # Get title in current language
        Article.objects.annotate(title_text=LocalizedRef('title'))

        # Get title in specific language
        Article.objects.annotate(title_en=LocalizedRef('title', 'en'))

        # Order by title in current language
        Article.objects.order_by(LocalizedRef('title').asc())

        # Use in values()
        Article.objects.values('id', title=LocalizedRef('title'))
    """

    def __init__(self, name: str, lang: str | None = None):
        """Initialize the expression.

        Args:
            name: The field/column name to select from.
            lang: The language code. Uses current language if not specified.
        """
        language = lang or translation.get_language() or settings.LANGUAGE_CODE
        super().__init__(language, F(name))


def L(name: str, lang: str | None = None) -> LocalizedRef:
    """Shorthand for LocalizedRef.

    Example:
        Article.objects.values('id', title=L('title'))
        Article.objects.order_by(L('title', 'en'))

    Args:
        name: The field/column name.
        lang: The language code.

    Returns:
        LocalizedRef expression.
    """
    return LocalizedRef(name, lang)
