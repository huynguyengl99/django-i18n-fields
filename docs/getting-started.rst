Getting Started
===============

This guide will help you get started with Django i18n Fields quickly and easily.

Quick Setup
-----------

Basic Django Configuration
---------------------------

1. **Add to INSTALLED_APPS**

Add ``i18n_fields`` to your ``INSTALLED_APPS``:

.. code-block:: python

    # settings.py
    INSTALLED_APPS = [
        # ... your existing apps
        'django.contrib.contenttypes',
        'django.contrib.auth',
        # ... other apps
        'i18n_fields',
    ]

2. **Configure Languages**

Set up the languages you want to support:

.. code-block:: python

    # settings.py
    from django.utils.translation import gettext_lazy as _

    LANGUAGE_CODE = 'en'

    LANGUAGES = [
        ('en', _('English')),
        ('es', _('Spanish')),
        ('fr', _('French')),
        ('de', _('German')),
    ]

3. **Create Your First Model**

Use localized fields in your models:

.. code-block:: python

    # models.py
    from django.db import models
    from i18n_fields import LocalizedCharField, LocalizedTextField

    class Article(models.Model):
        title = LocalizedCharField(required=['en'])
        content = LocalizedTextField(blank=True)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return str(self.title)

4. **Run Migrations**

Create and apply migrations:

.. code-block:: bash

    python manage.py makemigrations
    python manage.py migrate

Basic Usage
-----------

**Creating Objects**

.. code-block:: python

    # Create an article with translations
    article = Article.objects.create(
        title={
            'en': 'Hello World',
            'es': 'Hola Mundo',
            'fr': 'Bonjour le Monde'
        },
        content={
            'en': 'This is the content in English.',
            'es': 'Este es el contenido en español.',
        }
    )

**Accessing Values**

.. code-block:: python

    # Access in current language
    print(article.title)  # Returns value in active language

    # Access specific language
    print(article.title.get('es'))  # Returns 'Hola Mundo'

    # Use translation context
    from django.utils import translation

    with translation.override('es'):
        print(article.title)  # Returns 'Hola Mundo'

**Querying**

.. code-block:: python

    # Filter by specific language
    articles = Article.objects.filter(title__en='Hello World')

    # Order by title in current language
    from i18n_fields import L
    articles = Article.objects.order_by(L('title'))

Django Admin Setup
------------------

To use localized fields in Django admin, use the ``LocalizedFieldsAdminMixin``:

.. code-block:: python

    # admin.py
    from django.contrib import admin
    from i18n_fields import LocalizedFieldsAdminMixin
    from .models import Article

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        list_display = ['title', 'created_at']
        # Use 'tab' (default) or 'dropdown' for language switching
        localized_fields_display = 'tab'

The admin will automatically show tab or dropdown widgets for all localized fields.

Django REST Framework Setup
----------------------------

For REST API integration, use the ``LocalizedModelSerializer``:

.. code-block:: python

    # serializers.py
    from i18n_fields.drf import LocalizedModelSerializer
    from .models import Article

    class ArticleSerializer(LocalizedModelSerializer):
        class Meta:
            model = Article
            fields = ['id', 'title', 'content', 'created_at']

.. code-block:: python

    # views.py
    from rest_framework import viewsets
    from .models import Article
    from .serializers import ArticleSerializer

    class ArticleViewSet(viewsets.ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSerializer

The serializer will automatically return values in the active language:

.. code-block:: json

    {
        "id": 1,
        "title": "Hello World",
        "content": "This is the content in English.",
        "created_at": "2025-01-28T10:00:00Z"
    }

Optional Configuration
----------------------

You can customize Django i18n Fields behavior via settings:

.. code-block:: python

    # settings.py
    I18N_FIELDS = {
        # Admin display mode: "tab" or "dropdown"
        "DISPLAY": "tab",

        # Language fallback chains
        "FALLBACKS": {
            "nl": ["en"],  # If Dutch not available, fall back to English
            "fr": ["en"],  # If French not available, fall back to English
        },

        # Max retries for unique slug generation
        "MAX_RETRIES": 100,

        # Enable automatic lookup registration
        "REGISTER_LOOKUPS": True,
    }

For detailed configuration options, see :doc:`configuration`.

Next Steps
----------

- :doc:`user-guides/basic-usage` - Learn how to use localized fields effectively
- :doc:`user-guides/admin-integration` - Set up Django admin with localized fields
- :doc:`user-guides/drf-integration` - Integrate with Django REST Framework
- :doc:`user-guides/advanced-queries` - Advanced querying and filtering techniques
- :doc:`configuration` - Complete configuration reference
