Introduction
============

Django i18n Fields is a modern Django package that provides structured internationalization (i18n) for model fields. It allows you to store and manage multilingual content directly in your Django models using a clean, database-agnostic approach.

Why Choose Django i18n Fields?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Built as an Alternative to django-localized-fields**

Django i18n Fields is designed as an improved, actively maintained alternative to `django-localized-fields <https://github.com/SectorLabs/django-localized-fields>`_, which has been abandoned. It addresses several limitations while maintaining a similar API:

- **Database Agnostic**: Works with PostgreSQL, MySQL, SQLite, and any database that supports JSONField
- **Full Type Safety**: Complete type hints with mypy and pyright compatibility
- **Modern Django Support**: Built for Django 5.0+ with latest best practices
- **Enhanced Query Support**: Advanced filtering and ordering with query expressions
- **Better DRF Integration**: First-class Django REST Framework support with automatic serialization
- **Comprehensive Admin UI**: Beautiful tab and dropdown interfaces for managing translations
- **Active Maintenance**: Regular updates and bug fixes

Key Features
~~~~~~~~~~~~

**🌍 Comprehensive Field Types**

- CharField, TextField for text content
- IntegerField, FloatField, BooleanField for typed data
- FileField for multilingual file uploads
- UniqueSlugField with per-language uniqueness
- All fields support language-specific validation

**🎯 Flexible Storage**

- JSONField-based storage (works on all databases)
- No additional database tables required
- Efficient querying with JSON field lookups
- Support for language fallback chains

**📝 Rich Admin Integration**

- Tab-based or dropdown language switchers
- Automatic widget selection based on field type
- Read-only field support with proper display
- Works seamlessly with Django's admin interface

**🔍 Powerful Querying**

- Filter by specific language values
- Order by translated content
- Annotate queries with language-specific values
- Use expressions like ``L('field_name', 'en')`` for clean queries

**🚀 Django REST Framework Support**

- Automatic serialization in the active language
- ``LocalizedModelSerializer`` for easy integration
- Returns simple values instead of complex objects
- Seamless integration with DRF Spectacular for API docs

**🛠️ Developer Experience**

- **Full type hints** throughout the codebase
- **Comprehensive test coverage** (>95%)
- **Clean, maintainable code** with proper documentation
- **Easy migration** from django-localized-fields
- **Language fallback** support for missing translations

Architecture Overview
~~~~~~~~~~~~~~~~~~~~~

Django i18n Fields follows a clean, modular architecture:

**Core Components:**

1. **Field System**: Localized field types that extend Django's JSONField
2. **Value System**: Special value objects (``LocalizedValue``) that handle translation and fallbacks
3. **Descriptor System**: Python descriptors that provide natural attribute access
4. **Settings System**: Centralized configuration with lazy loading

**Optional Components:**

1. **Admin System**: Enhanced admin widgets and mixins for managing translations
2. **DRF System**: Serializers and fields for REST API integration
3. **Expression System**: Query expressions for database-level translation queries
4. **Lookup System**: Custom field lookups for filtering by language

**Design Principles:**

- **Database Agnostic**: No reliance on PostgreSQL-specific features
- **Type Safety**: Complete type hints for better IDE support and fewer bugs
- **Django Standards**: Follows Django's patterns and conventions
- **Easy to Use**: Minimal configuration with sensible defaults
- **Extensible**: Easy to customize and extend for specific needs

How It Works
~~~~~~~~~~~~

At its core, Django i18n Fields stores translations as JSON in a single database column:

.. code-block:: python

    # Model definition
    class Article(models.Model):
        title = LocalizedCharField(required=['en'])
        content = LocalizedTextField(blank=True)

.. code-block:: python

    # Database storage (as JSON)
    {
        "en": "Hello World",
        "es": "Hola Mundo",
        "fr": "Bonjour le Monde"
    }

.. code-block:: python

    # Python usage - automatic translation
    article = Article.objects.first()
    print(article.title)  # Returns "Hello World" (in English)

    with translation.override('es'):
        print(article.title)  # Returns "Hola Mundo" (in Spanish)

Getting Started
~~~~~~~~~~~~~~~

Ready to get started? Head over to the :doc:`installation` guide to install the package, then follow the :doc:`getting-started` guide for setup instructions.

**Quick Links:**

- :doc:`installation` - Installation instructions
- :doc:`getting-started` - Basic configuration and setup
- :doc:`user-guides/basic-usage` - Learn the core features
- :doc:`user-guides/admin-integration` - Set up Django admin
- :doc:`user-guides/drf-integration` - Integrate with Django REST Framework
- :doc:`user-guides/advanced-queries` - Advanced querying techniques

Comparison with django-localized-fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're migrating from django-localized-fields, here are the key differences:

**Improvements:**

- Works with all databases (not just PostgreSQL)
- Better type hints and IDE support
- Enhanced admin interface with tab/dropdown modes
- Built-in DRF support with serializers
- Query expressions (``L()`` and ``LocalizedRef``)
- Active maintenance and updates
- Better documentation

**API Compatibility:**

- Similar field names: ``LocalizedCharField``, ``LocalizedTextField``, etc.
- Compatible value access patterns
- Migration path available (see user guides)

Community and Support
~~~~~~~~~~~~~~~~~~~~~

**Contributing**

We welcome contributions! See our :doc:`contributing` guide for details on how to contribute to Django i18n Fields.

**Issues and Support**

- Report bugs or request features on `GitHub Issues <https://github.com/huynguyengl99/django-i18n-fields/issues>`_
- Check the documentation for common solutions
- Review the test cases for usage examples

**Changelog**

See the :doc:`changelog` for information about recent changes and updates.
