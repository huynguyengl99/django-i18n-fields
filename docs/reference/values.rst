Values Reference
================

This page documents the ``LocalizedValue`` classes that handle multilingual values.

LocalizedValue
--------------

Base class for all localized value types.

.. class:: LocalizedValue(keys=None)

   Dictionary-like object that stores values for multiple languages.

   **Parameters:**

   - ``keys`` (dict | None): Dictionary of language codes to values

   **Attributes:**

   - ``default_value``: Default value for missing languages (``None``)

   **Methods:**

   .. method:: get(language=None, default=None)

      Get value for a specific language.

      **Parameters:**

      - ``language`` (str | None): Language code (uses ``LANGUAGE_CODE`` if None)
      - ``default``: Default value if not found

      **Returns:** Value in the specified language or default

      **Example:**

      .. code-block:: python

          value = LocalizedValue({'en': 'Hello', 'es': 'Hola'})
          print(value.get('en'))  # 'Hello'
          print(value.get('fr', 'Not available'))  # 'Not available'

   .. method:: set(language, value)

      Set value for a specific language.

      **Parameters:**

      - ``language`` (str): Language code
      - ``value``: Value to set

      **Returns:** Self for chaining

      **Example:**

      .. code-block:: python

          value = LocalizedValue()
          value.set('en', 'Hello').set('es', 'Hola')

   .. method:: translate(language=None)

      Get value with fallback support.

      **Parameters:**

      - ``language`` (str | None): Target language (uses active language if None)

      **Returns:** Value in target language or fallback

      **Example:**

      .. code-block:: python

          # Configure fallbacks
          I18N_FIELDS = {
              "FALLBACKS": {"pt-br": ["pt", "en"]}
          }

          value = LocalizedValue({'en': 'Hello', 'pt': 'Olá'})

          with translation.override('pt-br'):
              # No pt-br, falls back to pt, then en
              print(value.translate())  # 'Olá'

   .. method:: is_empty()

      Check if all languages contain the default value.

      **Returns:** bool

      **Example:**

      .. code-block:: python

          value = LocalizedValue()
          print(value.is_empty())  # True

          value.set('en', 'Hello')
          print(value.is_empty())  # False

   **Dictionary Methods:**

   Supports standard dictionary operations:

   .. code-block:: python

       value = LocalizedValue({'en': 'Hello', 'es': 'Hola'})

       # Access like dict
       print(value['en'])  # 'Hello'

       # Iterate
       for lang, text in value.items():
           print(f"{lang}: {text}")

       # Check membership
       if 'en' in value:
           print("English available")

       # Get all languages
       languages = list(value.keys())

   **String Representation:**

   .. code-block:: python

       value = LocalizedValue({'en': 'Hello', 'es': 'Hola'})

       # Returns value in current language
       print(str(value))  # 'Hello' (if English is active)

       with translation.override('es'):
           print(str(value))  # 'Hola'

LocalizedStringValue
--------------------

.. class:: LocalizedStringValue(keys=None)

   LocalizedValue with empty string as default.

   **Default Value:** ``""`` (empty string)

   **Used By:**

   - ``LocalizedCharField``
   - ``LocalizedTextField``

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedStringValue

       # Create with dict
       value = LocalizedStringValue({
           'en': 'Hello',
           'es': 'Hola'
       })

       # Missing languages return empty string
       print(value.get('fr'))  # '' (not None)

       # Check for value
       if value.get('en'):
           print("English translation exists")

LocalizedIntegerValue
---------------------

.. class:: LocalizedIntegerValue(keys=None)

   LocalizedValue for integer fields.

   **Default Value:** ``None``

   **Used By:** ``LocalizedIntegerField``

   **Methods:**

   .. method:: translate()

      Get integer value with type conversion.

      **Returns:** int | None

      **Conversion Rules:**

      - ``int`` → returns as-is
      - ``str`` → converts to int (empty string returns None)
      - Other types → attempts int() conversion
      - Invalid → returns None

   **Magic Methods:**

   .. method:: __int__()

      Convert to integer (returns 0 if None).

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedIntegerValue

       value = LocalizedIntegerValue({
           'en': 100,
           'es': 50,
           'fr': '75'  # String is converted
       })

       print(value.translate())  # 100 (if English active)
       print(int(value))  # 100

       # Type conversion
       print(value.get('fr'))  # Returns 75 (converted from '75')

       # Missing value
       print(value.get('de'))  # None

LocalizedFloatValue
-------------------

.. class:: LocalizedFloatValue(keys=None)

   LocalizedValue for float fields.

   **Default Value:** ``None``

   **Used By:** ``LocalizedFloatField``

   **Methods:**

   .. method:: translate()

      Get float value with type conversion.

      **Returns:** float | None

      **Conversion Rules:**

      - ``float`` or ``int`` → converts to float
      - ``str`` → converts to float (empty string returns None)
      - Other types → attempts float() conversion
      - Invalid → returns None

   **Magic Methods:**

   .. method:: __float__()

      Convert to float (returns 0.0 if None).

   .. method:: __int__()

      Convert to integer (returns 0 if None).

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedFloatValue

       value = LocalizedFloatValue({
           'en': 99.99,
           'es': 89.99,
           'fr': '79.99'  # String is converted
       })

       print(value.translate())  # 99.99 (if English active)
       print(float(value))  # 99.99

       # Arithmetic operations
       price = float(value) * 1.1  # Apply 10% markup

LocalizedBooleanValue
---------------------

.. class:: LocalizedBooleanValue(keys=None)

   LocalizedValue for boolean fields.

   **Default Value:** ``None``

   **Used By:** ``LocalizedBooleanField``

   **Methods:**

   .. method:: translate()

      Get boolean value with type conversion.

      **Returns:** bool | None

      **Conversion Rules:**

      - ``bool`` → returns as-is
      - ``str`` → "true" (case-insensitive) returns True, empty returns None
      - Other types → converts using bool()

   **Magic Methods:**

   .. method:: __bool__()

      Convert to boolean (returns False if None).

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedBooleanValue

       value = LocalizedBooleanValue({
           'en': True,
           'es': False,
           'fr': 'true'  # String is converted
       })

       print(value.translate())  # True (if English active)
       print(bool(value))  # True

       # Use in conditionals
       if value:
           print("Value is truthy")

       # Type conversion
       print(value.get('fr'))  # True (converted from 'true')

LocalizedFileValue
------------------

.. class:: LocalizedFileValue(keys=None)

   LocalizedValue for file fields.

   **Default Value:** ``None``

   **Used By:** ``LocalizedFileField``

   **Methods:**

   .. method:: __getattr__(name)

      Proxy attribute access to the current language's file.

      **Returns:** Attribute from the file object

   **Example:**

   .. code-block:: python

       from i18n_fields import LocalizedFileValue

       # Assume files are uploaded
       value = LocalizedFileValue({
           'en': english_file,
           'es': spanish_file
       })

       # Access file properties in current language
       with translation.override('es'):
           url = value.url  # Proxies to spanish_file.url
           name = value.name
           size = value.size

       # Direct access
       en_url = value.get('en').url
       es_url = value.get('es').url

Type Conversions
----------------

Automatic Conversion
~~~~~~~~~~~~~~~~~~~~

LocalizedValue classes automatically convert values:

.. code-block:: python

    # Integer conversion
    int_value = LocalizedIntegerValue({'en': '100'})
    print(int_value.get('en'))  # 100 (converted from string)

    # Float conversion
    float_value = LocalizedFloatValue({'en': '99.99'})
    print(float_value.get('en'))  # 99.99 (converted from string)

    # Boolean conversion
    bool_value = LocalizedBooleanValue({'en': 'true'})
    print(bool_value.get('en'))  # True (converted from string)

Safe Conversion
~~~~~~~~~~~~~~~

Invalid values return None:

.. code-block:: python

    # Invalid integer
    int_value = LocalizedIntegerValue({'en': 'not a number'})
    print(int_value.get('en'))  # None

    # Invalid float
    float_value = LocalizedFloatValue({'en': 'invalid'})
    print(float_value.get('en'))  # None

    # Empty string
    int_value = LocalizedIntegerValue({'en': ''})
    print(int_value.get('en'))  # None

Creating Values
---------------

From Dictionary
~~~~~~~~~~~~~~~

.. code-block:: python

    from i18n_fields import LocalizedStringValue

    value = LocalizedStringValue({
        'en': 'Hello',
        'es': 'Hola',
        'fr': 'Bonjour'
    })

Using set() Method
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    value = LocalizedStringValue()
    value.set('en', 'Hello')
    value.set('es', 'Hola')
    value.set('fr', 'Bonjour')

Method Chaining
~~~~~~~~~~~~~~~

.. code-block:: python

    value = LocalizedStringValue().set('en', 'Hello').set('es', 'Hola')

From Model Field
~~~~~~~~~~~~~~~~

.. code-block:: python

    article = Article.objects.first()
    title_value = article.title  # Already a LocalizedValue

Comparing Values
----------------

Equality
~~~~~~~~

.. code-block:: python

    value1 = LocalizedStringValue({'en': 'Hello', 'es': 'Hola'})
    value2 = LocalizedStringValue({'en': 'Hello', 'es': 'Hola'})

    print(value1 == value2)  # True

    # Compare with string (uses current language)
    print(value1 == 'Hello')  # True (if English active)

Inequality
~~~~~~~~~~

.. code-block:: python

    value1 = LocalizedStringValue({'en': 'Hello'})
    value2 = LocalizedStringValue({'en': 'World'})

    print(value1 != value2)  # True

Iteration
---------

Iterate Over Languages
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    value = LocalizedStringValue({
        'en': 'Hello',
        'es': 'Hola',
        'fr': 'Bonjour'
    })

    # Iterate over items
    for lang, text in value.items():
        print(f"{lang}: {text}")

    # Iterate over keys
    for lang in value.keys():
        print(lang)

    # Iterate over values
    for text in value.values():
        print(text)

Serialization
-------------

To Dictionary
~~~~~~~~~~~~~

.. code-block:: python

    value = LocalizedStringValue({'en': 'Hello', 'es': 'Hola'})

    # Convert to dict
    data = dict(value)
    # {'en': 'Hello', 'es': 'Hola'}

For JSON
~~~~~~~~

.. code-block:: python

    import json

    value = LocalizedStringValue({'en': 'Hello', 'es': 'Hola'})

    # Serialize to JSON
    json_data = json.dumps(dict(value))
    # '{"en": "Hello", "es": "Hola"}'

Migration Support
-----------------

LocalizedValue classes support migrations:

.. code-block:: python

    # In migration
    value = LocalizedStringValue({'en': 'Default'})
    path, args, kwargs = value.deconstruct()
    # path: 'i18n_fields.value.LocalizedStringValue'
    # args: [{'en': 'Default'}]
    # kwargs: {}

Best Practices
--------------

1. **Use translate() for User-Facing Content**

   Always use ``translate()`` for fallback support:

   .. code-block:: python

       # Good - uses fallbacks
       display_text = article.title.translate()

       # Less ideal - no fallbacks
       display_text = str(article.title)

2. **Check for None**

   Numeric and boolean values can be None:

   .. code-block:: python

       # Good - check for None
       price = product.price.translate()
       if price is not None:
           print(f"Price: ${price}")

       # Bad - may fail if None
       print(f"Price: ${product.price}")

3. **Use Appropriate Type**

   Let the value class handle type conversion:

   .. code-block:: python

       # Good - automatic conversion
       stock = product.stock.get('en')  # Returns int

       # Unnecessary
       stock = int(product.stock.get('en'))

4. **Access with get() for Safety**

   Use ``get()`` with default for missing languages:

   .. code-block:: python

       # Good - provides default
       title = article.title.get('fr', 'No translation')

       # May return None
       title = article.title.get('fr')

See Also
--------

- :doc:`fields` - Localized field types
- :doc:`../user-guides/basic-usage` - Basic usage examples
- :doc:`../configuration` - Fallback configuration
