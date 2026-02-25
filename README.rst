DJANGO i18n FIELDS
==================

.. image:: https://img.shields.io/pypi/v/django-i18n-fields
   :target: https://pypi.org/project/django-i18n-fields/
   :alt: PyPI

.. image:: https://codecov.io/gh/huynguyengl99/django-i18n-fields/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/huynguyengl99/django-i18n-fields
   :alt: Code Coverage

.. image:: https://github.com/huynguyengl99/django-i18n-fields/actions/workflows/test.yml/badge.svg?branch=main
   :target: https://github.com/huynguyengl99/django-i18n-fields/actions/workflows/test.yml
   :alt: Test

.. image:: https://www.mypy-lang.org/static/mypy_badge.svg
   :target: https://mypy-lang.org/
   :alt: Checked with mypy

.. image:: https://microsoft.github.io/pyright/img/pyright_badge.svg
   :target: https://microsoft.github.io/pyright/
   :alt: Checked with pyright

A modern Django package providing structured internationalization (i18n) for model fields. Store and manage multilingual content directly in your Django models using a clean, database-agnostic approach.

**Improved alternative to django-localized-fields** - Works with all databases, not just PostgreSQL.

Key Features
------------

🌍 **Comprehensive Field Types**
   CharField, TextField, IntegerField, FloatField, BooleanField, FileField, UniqueSlugField, and MartorField (Markdown) with multilingual support

🎯 **Database Agnostic**
   Works with PostgreSQL, MySQL, SQLite - any database that supports JSONField

📝 **Rich Admin Integration**
   Beautiful tab and dropdown interfaces for managing translations in Django admin, with Markdown editor support via `martor <https://github.com/agusmakmun/django-markdown-editor>`_

🔍 **Powerful Querying**
   Filter, order, and annotate queries with language-specific values using ``L()`` expressions

🚀 **Django REST Framework Support**
   Automatic serialization with ``LocalizedModelSerializer`` - returns simple values in the active language

🛠️ **Full Type Safety**
   Complete type hints with mypy and pyright compatibility

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

    pip install django-i18n-fields

    # With Markdown editor support (martor)
    pip install django-i18n-fields[md]

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    # models.py
    from django.db import models
    from i18n_fields import LocalizedCharField, LocalizedTextField

    class Article(models.Model):
        title = LocalizedCharField(max_length=200, required=['en'])
        content = LocalizedTextField(blank=True)

    # Create with translations
    article = Article.objects.create(
        title={'en': 'Hello World', 'es': 'Hola Mundo'},
        content={'en': 'Content in English', 'es': 'Contenido en español'}
    )

    # Access in current language
    print(article.title)  # Automatically uses active language

    # Query by specific language
    Article.objects.filter(title__en='Hello World')

    # Order by translated field
    from i18n_fields import L
    Article.objects.order_by(L('title'))

Django Admin
~~~~~~~~~~~~

.. code-block:: python

    # admin.py - Option 1: Using the base class (recommended)
    from i18n_fields import LocalizedFieldsAdmin

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdmin):
        list_display = ['title', 'created_at']
        # Automatic tab/dropdown widgets for all localized fields!

    # admin.py - Option 2: Using the mixin with your own base class
    from django.contrib import admin
    from i18n_fields import LocalizedFieldsAdminMixin

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        list_display = ['title', 'created_at']

Django REST Framework
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # serializers.py
    from i18n_fields.drf import LocalizedModelSerializer

    class ArticleSerializer(LocalizedModelSerializer):
        class Meta:
            model = Article
            fields = ['id', 'title', 'content']

    # Returns: {"id": 1, "title": "Hello World", "content": "..."}
    # Automatically uses active language!

Configuration
~~~~~~~~~~~~~

.. code-block:: python

    # settings.py
    INSTALLED_APPS = [
        # ...
        'i18n_fields',
    ]

    LANGUAGES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
    ]

    I18N_FIELDS = {
        'DISPLAY': 'tab',  # or 'dropdown' for admin
        'FALLBACKS': {
            'en-us': ['en'],
            'es-mx': ['es'],
        },
    }

Why Django i18n Fields?
-----------------------

**vs django-localized-fields**

- ✅ Works with **all databases** (not just PostgreSQL)
- ✅ **Actively maintained** with regular updates
- ✅ **Better type hints** and IDE support
- ✅ **Built-in DRF support** with automatic serialization
- ✅ **Enhanced admin UI** with tab/dropdown modes
- ✅ **Query expressions** (``L()`` and ``LocalizedRef``)
- ✅ **Comprehensive documentation**

Documentation
-------------

📚 **Full documentation**: https://django-i18n-fields.readthedocs.io/

**Quick Links:**

- `Installation <https://django-i18n-fields.readthedocs.io/en/latest/installation.html>`_
- `Getting Started <https://django-i18n-fields.readthedocs.io/en/latest/getting-started.html>`_
- `User Guides <https://django-i18n-fields.readthedocs.io/en/latest/user-guides/basic-usage.html>`_
- `API Reference <https://django-i18n-fields.readthedocs.io/en/latest/reference/fields.html>`_

Requirements
------------

- Python 3.10+
- Django 5.0+
- Django REST Framework 3.0+ (optional, for DRF integration)
- martor (optional, for Markdown editor support — install with ``pip install django-i18n-fields[md]``)

Contributing
------------

We welcome contributions! Please see our `Contributing Guide <https://github.com/huynguyengl99/django-i18n-fields/blob/main/CONTRIBUTING.md>`_ for detailed instructions.

**Development Setup:**

.. code-block:: bash

    git clone https://github.com/huynguyengl99/django-i18n-fields.git
    cd django-i18n-fields
    uv venv
    source .venv/bin/activate
    uv sync --all-extras
    pytest

License
-------

MIT License - see `LICENSE <https://github.com/huynguyengl99/django-i18n-fields/blob/main/LICENSE>`_ for details.

Support
-------

- 🐛 **Bug Reports**: `GitHub Issues <https://github.com/huynguyengl99/django-i18n-fields/issues>`_
- 💬 **Questions**: `GitHub Discussions <https://github.com/huynguyengl99/django-i18n-fields/discussions>`_
- 📖 **Documentation**: https://django-i18n-fields.readthedocs.io/
