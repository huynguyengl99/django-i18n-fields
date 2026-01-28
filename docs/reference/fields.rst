Fields Reference
================

This page documents all localized field types provided by Django i18n Fields.

LocalizedField
--------------

Base class for all localized fields.

.. class:: LocalizedField(**options)

   A field that stores localized values in multiple languages using JSONField.

   **Parameters:**

   - ``required`` (bool | list[str] | None): Languages that require a value.

     - ``None`` with ``blank=True``: No languages required
     - ``None`` with ``blank=False``: Primary language (``LANGUAGE_CODE``) required
     - ``True``: All configured languages required
     - ``False``: No languages required
     - ``List[str]``: Specific languages required (e.g., ``['en', 'es']``)

   - Standard Django field options: ``blank``, ``null``, ``default``, etc.

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedField

       class MyModel(models.Model):
           # Require English
           field1 = LocalizedField(required=['en'])

           # Require all languages
           field2 = LocalizedField(required=True)

           # No languages required
           field3 = LocalizedField(blank=True)

   **Methods:**

   .. method:: from_db_value(value, expression, connection)

      Converts database value to LocalizedValue instance.

   .. method:: to_python(value)

      Converts value to LocalizedValue instance.

   .. method:: get_prep_value(value)

      Prepares LocalizedValue for database storage.

LocalizedCharField
------------------

.. class:: LocalizedCharField(max_length, **options)

   Localized version of Django's ``CharField``.

   **Parameters:**

   - ``max_length`` (int): Maximum length for each translation
   - All ``LocalizedField`` options

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedCharField

       class Article(models.Model):
           title = LocalizedCharField(
               max_length=200,
               required=['en'],
               help_text="Article title in multiple languages"
           )

   **Value Type:** Returns ``LocalizedStringValue``

   **Storage:** JSON with empty string as default for missing translations

LocalizedTextField
------------------

.. class:: LocalizedTextField(**options)

   Localized version of Django's ``TextField``.

   **Parameters:**

   - All ``LocalizedField`` options

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedTextField

       class Article(models.Model):
           content = LocalizedTextField(
               blank=True,
               help_text="Article content"
           )

           description = LocalizedTextField(
               required=['en', 'es']
           )

   **Value Type:** Returns ``LocalizedStringValue``

   **Usage:**

   .. code-block:: python

       article = Article.objects.create(
           content={
               'en': 'Long content in English...',
               'es': 'Contenido largo en español...'
           }
       )

       print(article.content)  # Returns translated content

LocalizedIntegerField
---------------------

.. class:: LocalizedIntegerField(**options)

   Localized version of Django's ``IntegerField``.

   **Parameters:**

   - All ``LocalizedField`` options

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedIntegerField

       class Product(models.Model):
           stock = LocalizedIntegerField(
               blank=True,
               help_text="Stock quantity by region"
           )

   **Value Type:** Returns ``LocalizedIntegerValue``

   **Usage:**

   .. code-block:: python

       product = Product.objects.create(
           stock={
               'en': 100,  # US stock
               'es': 50,   # Spain stock
               'fr': 75    # France stock
           }
       )

       # Get current language value
       print(product.stock)  # Returns integer

       # Get specific language
       print(product.stock.get('es'))  # Returns 50

LocalizedFloatField
-------------------

.. class:: LocalizedFloatField(**options)

   Localized version of Django's ``FloatField``.

   **Parameters:**

   - All ``LocalizedField`` options

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedFloatField

       class Product(models.Model):
           price = LocalizedFloatField(
               blank=True,
               help_text="Price in local currency"
           )

           rating = LocalizedFloatField(
               null=True,
               blank=True
           )

   **Value Type:** Returns ``LocalizedFloatValue``

   **Usage:**

   .. code-block:: python

       product = Product.objects.create(
           price={
               'en': 99.99,   # USD
               'es': 89.99,   # EUR
               'jp': 10999.0  # JPY
           }
       )

       with translation.override('es'):
           print(product.price)  # Returns 89.99

LocalizedBooleanField
---------------------

.. class:: LocalizedBooleanField(**options)

   Localized version of Django's ``BooleanField``.

   **Parameters:**

   - All ``LocalizedField`` options

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedBooleanField

       class Feature(models.Model):
           is_enabled = LocalizedBooleanField(
               blank=True,
               help_text="Feature enabled by region"
           )

   **Value Type:** Returns ``LocalizedBooleanValue``

   **Usage:**

   .. code-block:: python

       feature = Feature.objects.create(
           is_enabled={
               'en': True,   # Enabled in US
               'es': False,  # Disabled in Spain
               'fr': True    # Enabled in France
           }
       )

       with translation.override('es'):
           if feature.is_enabled:
               print("Feature is enabled")

LocalizedFileField
------------------

.. class:: LocalizedFileField(upload_to, **options)

   Localized version of Django's ``FileField``.

   **Parameters:**

   - ``upload_to`` (str | callable): Upload path
   - All ``LocalizedField`` options

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedFileField

       class Document(models.Model):
           file = LocalizedFileField(
               upload_to='documents/%Y/%m/',
               blank=True,
               help_text="Document file in multiple languages"
           )

   **Value Type:** Returns ``LocalizedFileValue``

   **Usage:**

   .. code-block:: python

       # Upload files
       document = Document.objects.create(
           file={
               'en': english_file,
               'es': spanish_file,
               'fr': french_file
           }
       )

       # Access file in current language
       with translation.override('es'):
           url = document.file.url
           name = document.file.name
           size = document.file.size

LocalizedUniqueSlugField
------------------------

.. class:: LocalizedUniqueSlugField(populate_from, **options)

   Localized slug field with automatic generation and per-language uniqueness.

   **Parameters:**

   - ``populate_from`` (str | callable): Field name or callable to generate slug from
   - All ``LocalizedField`` options

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedUniqueSlugField, AtomicSlugRetryMixin

       class Article(models.Model, AtomicSlugRetryMixin):
           title = LocalizedCharField(max_length=200, required=['en'])
           slug = LocalizedUniqueSlugField(
               populate_from='title',
               unique=True
           )

   **Value Type:** Returns ``LocalizedStringValue``

   **Features:**

   - Automatic slug generation from ``populate_from`` field
   - Per-language uniqueness
   - Automatic retry with incrementing numbers on conflicts
   - Uses ``MAX_RETRIES`` setting for retry limit

   **Usage:**

   .. code-block:: python

       # Slug generated automatically
       article = Article.objects.create(
           title={
               'en': 'Hello World',
               'es': 'Hola Mundo'
           }
       )

       # Slugs: {'en': 'hello-world', 'es': 'hola-mundo'}
       print(article.slug.en)  # 'hello-world'
       print(article.slug.es)  # 'hola-mundo'

       # Conflict handling
       article2 = Article.objects.create(
           title={'en': 'Hello World'}
       )
       # Slug: {'en': 'hello-world-2'}

   **With Mixin:**

   Use ``AtomicSlugRetryMixin`` for atomic slug generation:

   .. code-block:: python

       from i18n_fields import AtomicSlugRetryMixin

       class Article(models.Model, AtomicSlugRetryMixin):
           slug = LocalizedUniqueSlugField(populate_from='title')

Field Options
-------------

Common Options
~~~~~~~~~~~~~~

All localized fields accept standard Django field options:

- ``null`` (bool): If ``True``, empty values are stored as NULL
- ``blank`` (bool): If ``True``, field is not required in forms
- ``default``: Default value for the field
- ``help_text`` (str): Help text for forms
- ``verbose_name`` (str): Human-readable name
- ``db_column`` (str): Database column name
- ``db_index`` (bool): Create database index
- ``editable`` (bool): Show in forms/admin

Required Option
~~~~~~~~~~~~~~~

The ``required`` parameter is specific to localized fields:

.. code-block:: python

    # No languages required
    field = LocalizedCharField(blank=True)

    # Primary language required
    field = LocalizedCharField(required=['en'])

    # Multiple languages required
    field = LocalizedCharField(required=['en', 'es', 'fr'])

    # All configured languages required
    field = LocalizedCharField(required=True)

Validation
----------

Required Language Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Localized fields validate that required languages have values:

.. code-block:: python

    class Article(models.Model):
        title = LocalizedCharField(required=['en', 'es'])

    # This will raise IntegrityError
    article = Article.objects.create(
        title={'en': 'Hello'}  # Missing required 'es'
    )

Null Validation
~~~~~~~~~~~~~~~

When ``null=False``, at least one language must have a value:

.. code-block:: python

    class Article(models.Model):
        title = LocalizedCharField(null=False, blank=True)

    # This is OK - has at least one value
    article = Article.objects.create(
        title={'en': 'Hello'}
    )

    # This will raise error - all values are None
    article = Article.objects.create(
        title={'en': None, 'es': None}
    )

Migration Support
-----------------

All localized fields support Django migrations:

.. code-block:: python

    # Generated migration
    operations = [
        migrations.AddField(
            model_name='article',
            name='title',
            field=i18n_fields.fields.LocalizedCharField(
                max_length=200,
                required=['en']
            ),
        ),
    ]

Best Practices
--------------

1. **Choose Appropriate Field Type**

   Use the field type that matches your data:

   .. code-block:: python

       # Text content
       title = LocalizedCharField(max_length=200)
       content = LocalizedTextField()

       # Numbers
       price = LocalizedFloatField()
       stock = LocalizedIntegerField()

       # Booleans
       is_active = LocalizedBooleanField()

2. **Set Required Languages Carefully**

   Only require languages you can guarantee:

   .. code-block:: python

       # Good - only require primary language
       title = LocalizedCharField(required=['en'])

       # Be careful - requires multiple languages
       title = LocalizedCharField(required=['en', 'es', 'fr'])

3. **Use Appropriate Defaults**

   Set defaults for optional fields:

   .. code-block:: python

       rating = LocalizedFloatField(blank=True, default=0.0)
       is_featured = LocalizedBooleanField(default=False)

4. **Consider null vs blank**

   - Use ``blank=True`` for optional fields in forms
   - Use ``null=True`` to allow NULL in database

   .. code-block:: python

       # Optional in forms, empty string in DB
       description = LocalizedTextField(blank=True)

       # Optional in forms, NULL in DB
       notes = LocalizedTextField(blank=True, null=True)

See Also
--------

- :doc:`values` - LocalizedValue classes
- :doc:`../user-guides/basic-usage` - Basic usage examples
- :doc:`../user-guides/admin-integration` - Admin integration
