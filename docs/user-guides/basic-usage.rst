Basic Usage
===========

This guide covers the basic usage patterns for Django i18n Fields.

Defining Localized Fields
--------------------------

Field Types
~~~~~~~~~~~

Django i18n Fields provides localized versions of common Django field types:

.. code-block:: python

    from django.db import models
    from i18n_fields import (
        LocalizedCharField,
        LocalizedTextField,
        LocalizedIntegerField,
        LocalizedFloatField,
        LocalizedBooleanField,
        LocalizedFileField,
        LocalizedUniqueSlugField,
    )

    class Product(models.Model):
        name = LocalizedCharField(max_length=200, required=['en'])
        description = LocalizedTextField(blank=True)
        price = LocalizedFloatField(blank=True)
        stock = LocalizedIntegerField(blank=True)
        is_available = LocalizedBooleanField(blank=True)
        image = LocalizedFileField(upload_to='products/', blank=True)
        slug = LocalizedUniqueSlugField(populate_from='name')

Field Options
~~~~~~~~~~~~~

All localized fields accept standard Django field options plus localization-specific options:

.. code-block:: python

    class Article(models.Model):
        # Required: Specific languages must have values
        title = LocalizedCharField(
            required=['en', 'es'],  # English and Spanish required
            max_length=200
        )

        # Blank: All languages optional
        subtitle = LocalizedCharField(
            blank=True,
            max_length=200
        )

        # Required=True: All configured languages required
        slug = LocalizedCharField(
            required=True,
            max_length=100
        )

        # Null: Can be None in database
        notes = LocalizedTextField(
            blank=True,
            null=True
        )

Creating Objects
----------------

Dictionary Assignment
~~~~~~~~~~~~~~~~~~~~~

The most straightforward way to create objects:

.. code-block:: python

    article = Article.objects.create(
        title={
            'en': 'Hello World',
            'es': 'Hola Mundo',
            'fr': 'Bonjour le Monde'
        },
        content={
            'en': 'Content in English',
            'es': 'Contenido en español'
        }
    )

LocalizedValue Objects
~~~~~~~~~~~~~~~~~~~~~~

You can also use ``LocalizedValue`` objects directly:

.. code-block:: python

    from i18n_fields import LocalizedStringValue

    title_value = LocalizedStringValue()
    title_value.set('en', 'Hello World')
    title_value.set('es', 'Hola Mundo')

    article = Article.objects.create(title=title_value)

String Assignment
~~~~~~~~~~~~~~~~~

Assigning a string sets the value for the primary language:

.. code-block:: python

    # Sets value for LANGUAGE_CODE (default language)
    article = Article.objects.create(
        title='Hello World'  # Only sets English
    )

Accessing Values
----------------

Automatic Translation
~~~~~~~~~~~~~~~~~~~~~

Access fields like regular model attributes. The value automatically translates to the active language:

.. code-block:: python

    article = Article.objects.first()

    # Returns value in active language
    print(article.title)  # "Hello World" (if English is active)

    # Use translation context
    from django.utils import translation

    with translation.override('es'):
        print(article.title)  # "Hola Mundo"

Specific Language Access
~~~~~~~~~~~~~~~~~~~~~~~~~

Access values in specific languages:

.. code-block:: python

    # Using get()
    english_title = article.title.get('en')
    spanish_title = article.title.get('es')

    # Using attribute access
    english_title = article.title.en
    spanish_title = article.title.es

    # With fallback
    value = article.title.get('pt', default='Not available')

Translation with Fallback
~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``translate()`` method for fallback support:

.. code-block:: python

    # Configure fallbacks in settings
    I18N_FIELDS = {
        "FALLBACKS": {
            "pt-br": ["pt", "en"],
        }
    }

    # Create article with limited translations
    article = Article.objects.create(
        title={
            'en': 'Hello',
            'es': 'Hola'
        }
    )

    # Falls back to English if Brazilian Portuguese not available
    with translation.override('pt-br'):
        print(article.title.translate())  # "Hello"

Updating Values
---------------

Update Entire Field
~~~~~~~~~~~~~~~~~~~

Replace all translations at once:

.. code-block:: python

    article.title = {
        'en': 'Updated Title',
        'es': 'Título Actualizado',
        'fr': 'Titre Mis à Jour'
    }
    article.save()

Update Single Language
~~~~~~~~~~~~~~~~~~~~~~

Update just one language while preserving others:

.. code-block:: python

    # Get current value
    title = article.title

    # Update Spanish only
    title.set('es', 'Nuevo Título')

    # Save back to model
    article.title = title
    article.save()

Partial Updates
~~~~~~~~~~~~~~~

Update specific fields:

.. code-block:: python

    # Update using update()
    Article.objects.filter(pk=article.pk).update(
        title={'en': 'New Title', 'es': 'Nuevo Título'}
    )

Querying
--------

Basic Filtering
~~~~~~~~~~~~~~~

Filter by values in specific languages:

.. code-block:: python

    # Filter by English title
    articles = Article.objects.filter(title__en='Hello World')

    # Case-insensitive search
    articles = Article.objects.filter(title__en__icontains='hello')

    # Filter by multiple languages
    articles = Article.objects.filter(
        title__en='Hello',
        title__es='Hola'
    )

Ordering
~~~~~~~~

Order by localized fields:

.. code-block:: python

    from i18n_fields import L

    # Order by current language
    articles = Article.objects.order_by(L('title'))

    # Order by specific language
    articles = Article.objects.order_by(L('title', 'en'))

    # Descending order
    articles = Article.objects.order_by(L('title').desc())

Annotations
~~~~~~~~~~~

Annotate queries with localized values:

.. code-block:: python

    from i18n_fields import LocalizedRef

    # Annotate with current language
    articles = Article.objects.annotate(
        title_text=LocalizedRef('title')
    )

    # Annotate with specific language
    articles = Article.objects.annotate(
        title_en=LocalizedRef('title', 'en'),
        title_es=LocalizedRef('title', 'es')
    )

Values Queries
~~~~~~~~~~~~~~

Use with values() and values_list():

.. code-block:: python

    # Get specific language values
    titles = Article.objects.values('id', title=L('title', 'en'))

    # Get multiple languages
    data = Article.objects.values(
        'id',
        title_en=L('title', 'en'),
        title_es=L('title', 'es')
    )

Forms
-----

ModelForm Integration
~~~~~~~~~~~~~~~~~~~~~

Localized fields work seamlessly with Django ModelForms:

.. code-block:: python

    from django import forms
    from .models import Article

    class ArticleForm(forms.ModelForm):
        class Meta:
            model = Article
            fields = ['title', 'content']

The form will automatically generate widgets for all configured languages.

Validation
~~~~~~~~~~

Required language validation happens automatically:

.. code-block:: python

    # This will raise ValidationError if English is missing
    form = ArticleForm(data={
        'title': {'es': 'Hola'},  # Missing required 'en'
    })

    if form.is_valid():
        article = form.save()
    else:
        print(form.errors)  # Shows validation errors

Templates
---------

Displaying Localized Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In templates, localized fields automatically use the active language:

.. code-block:: django

    {% load i18n %}

    <h1>{{ article.title }}</h1>
    <p>{{ article.content }}</p>

    {% language 'es' %}
        <h1>{{ article.title }}</h1>  <!-- Shows Spanish -->
    {% endlanguage %}

Accessing Specific Languages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: django

    <h1>English: {{ article.title.en }}</h1>
    <h1>Spanish: {{ article.title.es }}</h1>
    <h1>French: {{ article.title.fr }}</h1>

Checking if Translation Exists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: django

    {% if article.title.en %}
        <p>English translation available</p>
    {% endif %}

Best Practices
--------------

1. **Use Required Languages Wisely**

   Only mark languages as required if you can guarantee content:

   .. code-block:: python

       # Good: Only require primary language
       title = LocalizedCharField(required=['en'])

       # Consider carefully: Multiple required languages
       title = LocalizedCharField(required=['en', 'es', 'fr'])

2. **Provide Fallback Chains**

   Configure fallbacks for regional variants:

   .. code-block:: python

       I18N_FIELDS = {
           "FALLBACKS": {
               "en-us": ["en"],
               "es-mx": ["es"],
               "pt-br": ["pt", "en"],
           }
       }

3. **Use translate() for User-Facing Content**

   Use the translate() method to ensure fallbacks work:

   .. code-block:: python

       # Good: Uses fallbacks
       display_text = article.title.translate()

       # Less ideal: No fallbacks
       display_text = str(article.title)

4. **Bulk Operations**

   For bulk updates, update specific languages:

   .. code-block:: python

       # Update English titles in bulk
       Article.objects.filter(category='news').update(
           title={'en': 'Breaking News'}
       )

Next Steps
----------

- :doc:`admin-integration` - Set up Django admin with localized fields
- :doc:`drf-integration` - Integrate with Django REST Framework
- :doc:`advanced-queries` - Learn advanced querying techniques
- :doc:`../reference/fields` - Complete field reference
