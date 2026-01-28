"""Django app configuration for articles."""

from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    """App configuration for articles."""

    name = "articles"
    verbose_name = "Articles"
    default_auto_field = "django.db.models.BigAutoField"
