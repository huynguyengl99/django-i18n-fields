"""Django REST Framework integration for i18n_fields.

This module provides DRF serializer support for localized fields.

Example:
    from i18n_fields.drf import LocalizedModelSerializer

    class ArticleSerializer(LocalizedModelSerializer):
        class Meta:
            model = Article
            fields = ['id', 'title', 'content']
"""

from .serializers import LocalizedModelSerializer

__all__ = [
    "LocalizedModelSerializer",
]
