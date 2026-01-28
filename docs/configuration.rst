Configuration
=============

Django i18n Fields can be configured through the ``I18N_FIELDS`` dictionary in your Django settings.

All settings are optional and have sensible defaults.

Settings Reference
------------------

DISPLAY
~~~~~~~

**Type**: ``Literal["tab", "dropdown"]``

**Default**: ``"tab"``

**Description**: Controls the display mode for localized fields in Django admin.

- ``"tab"``: Shows language tabs above the input field (default)
- ``"dropdown"``: Shows a dropdown menu to select the language

.. code-block:: python

    I18N_FIELDS = {
        "DISPLAY": "dropdown",  # or "tab"
    }

**Usage**: This setting affects the admin widget display for all localized fields unless overridden in individual admin classes.

FALLBACKS
~~~~~~~~~

**Type**: ``dict[str, list[str]]``

**Default**: ``{}``

**Description**: Defines language fallback chains. When a translation is missing in a language, the system will try languages in the fallback chain.

.. code-block:: python

    I18N_FIELDS = {
        "FALLBACKS": {
            "nl": ["en"],           # Dutch -> English
            "fr": ["en"],           # French -> English
            "pt-br": ["pt", "en"],  # Brazilian Portuguese -> Portuguese -> English
        },
    }

**Example**:

.. code-block:: python

    # With FALLBACKS configured as above
    article = Article.objects.create(
        title={'en': 'Hello', 'pt': 'Olá'}
    )

    with translation.override('pt-br'):
        # No 'pt-br' translation, falls back to 'pt', then 'en'
        print(article.title)  # Returns 'Olá'

    with translation.override('nl'):
        # No 'nl' translation, falls back to 'en'
        print(article.title)  # Returns 'Hello'

MAX_RETRIES
~~~~~~~~~~~

**Type**: ``int``

**Default**: ``100``

**Description**: Maximum number of retries when generating unique slugs with ``LocalizedUniqueSlugField``.

.. code-block:: python

    I18N_FIELDS = {
        "MAX_RETRIES": 200,
    }

**Usage**: If a slug conflict occurs, the field will append numbers (e.g., ``slug-2``, ``slug-3``) until a unique slug is found or MAX_RETRIES is reached.

REGISTER_LOOKUPS
~~~~~~~~~~~~~~~~

**Type**: ``bool``

**Default**: ``True``

**Description**: Whether to automatically register custom field lookups for localized fields.

.. code-block:: python

    I18N_FIELDS = {
        "REGISTER_LOOKUPS": False,  # Disable automatic lookup registration
    }

**Usage**: When ``True``, allows filtering by specific languages:

.. code-block:: python

    # With REGISTER_LOOKUPS=True
    Article.objects.filter(title__en='Hello')
    Article.objects.filter(title__en__icontains='hello')

Complete Example
----------------

Here's a complete example with all settings:

.. code-block:: python

    # settings.py
    from django.utils.translation import gettext_lazy as _

    # Django language settings
    LANGUAGE_CODE = 'en'

    LANGUAGES = [
        ('en', _('English')),
        ('es', _('Spanish')),
        ('fr', _('French')),
        ('de', _('German')),
        ('pt', _('Portuguese')),
        ('pt-br', _('Brazilian Portuguese')),
    ]

    # Django i18n Fields configuration
    I18N_FIELDS = {
        # Admin interface display mode
        "DISPLAY": "tab",

        # Language fallback chains
        "FALLBACKS": {
            "en-us": ["en"],
            "en-gb": ["en"],
            "pt-br": ["pt", "en"],
            "es-mx": ["es", "en"],
            "fr-ca": ["fr", "en"],
        },

        # Max retries for unique slug generation
        "MAX_RETRIES": 100,

        # Enable field lookups
        "REGISTER_LOOKUPS": True,
    }

Per-Admin Configuration
-----------------------

You can override the global ``DISPLAY`` setting for specific admin classes:

.. code-block:: python

    from django.contrib import admin
    from i18n_fields import LocalizedFieldsAdminMixin
    from .models import Article, BlogPost

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        # Use tab display for this admin
        localized_fields_display = 'tab'

    @admin.register(BlogPost)
    class BlogPostAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        # Use dropdown display for this admin
        localized_fields_display = 'dropdown'

Per-Field Configuration
-----------------------

Each localized field can be configured with its own options:

**required Parameter**

Controls which languages are required:

.. code-block:: python

    from i18n_fields import LocalizedCharField

    class Article(models.Model):
        # Require English only
        title = LocalizedCharField(required=['en'])

        # Require English and Spanish
        subtitle = LocalizedCharField(required=['en', 'es'])

        # Require all configured languages
        slug = LocalizedCharField(required=True)

        # No languages required (all optional)
        description = LocalizedCharField(blank=True)

**blank and null Parameters**

Control whether the field can be empty:

.. code-block:: python

    class Article(models.Model):
        # Required field (at least one language must have a value)
        title = LocalizedCharField(required=['en'])

        # Optional field (can be completely empty)
        description = LocalizedTextField(blank=True, null=True)

        # Optional with fallback to empty string
        notes = LocalizedTextField(blank=True)

Best Practices
--------------

**1. Define Fallback Chains**

Always define fallback chains for regional language variants:

.. code-block:: python

    I18N_FIELDS = {
        "FALLBACKS": {
            # Regional variants fall back to base language
            "en-us": ["en"],
            "en-gb": ["en"],
            "es-mx": ["es"],
            "pt-br": ["pt"],
        },
    }

**2. Choose Required Languages Carefully**

Only mark languages as required if you can guarantee translations:

.. code-block:: python

    # Good: Only require primary language
    title = LocalizedCharField(required=['en'])

    # Be careful: Requiring multiple languages
    title = LocalizedCharField(required=['en', 'es', 'fr'])

**3. Use Consistent Display Mode**

Choose one display mode (tab or dropdown) and use it consistently across your admin:

.. code-block:: python

    # settings.py
    I18N_FIELDS = {
        "DISPLAY": "tab",  # Use tabs everywhere
    }

**4. Test Fallback Chains**

Always test your fallback chains to ensure they work as expected:

.. code-block:: python

    # Create test data
    article = Article.objects.create(
        title={'en': 'Hello', 'es': 'Hola'}
    )

    # Test fallbacks
    with translation.override('pt-br'):
        assert str(article.title) == 'Hello'  # Falls back to English

Dynamic Settings Reload
-----------------------

Settings are automatically reloaded when Django settings change. This is useful during development:

.. code-block:: python

    from i18n_fields import i18n_fields_settings

    # Access current settings
    print(i18n_fields_settings.DISPLAY)

    # Settings reload automatically when Django settings change
    # No manual reload needed in production

Next Steps
----------

- :doc:`user-guides/basic-usage` - Learn how to use the configured fields
- :doc:`user-guides/admin-integration` - Set up Django admin
- :doc:`user-guides/advanced-queries` - Advanced querying with configured fallbacks
