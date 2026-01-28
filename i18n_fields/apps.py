"""Django app configuration for i18n_fields."""

from django.apps import AppConfig


class I18nFieldsConfig(AppConfig):
    """App configuration for i18n_fields."""

    name = "i18n_fields"
    verbose_name = "I18n Fields"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """Register lookups when the app is ready."""
        from .fields import LocalizedField
        from .lookups import register_lookups
        from .settings import i18n_fields_settings

        if i18n_fields_settings.REGISTER_LOOKUPS:
            register_lookups(LocalizedField)
