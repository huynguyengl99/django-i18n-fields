Installation
============

Dependencies
------------

Django i18n Fields has minimal dependencies:

**Core Dependencies**:

- **Django** (>=5.0) - Web framework with JSONField support
- **Python** (>=3.10) - Modern Python version

**Optional Dependencies**:

- **martor** - For Markdown editor support (``LocalizedMartorField``)

Installation Options
--------------------

Basic Installation
~~~~~~~~~~~~~~~~~~

Install Django i18n Fields using pip:

.. code-block:: bash

    pip install django-i18n-fields

With Markdown Editor Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use ``LocalizedMartorField`` for Markdown editing with `martor <https://github.com/agusmakmun/django-markdown-editor>`_ (`docs <https://django-markdown-editor.readthedocs.io/en/latest/index.html>`_):

.. code-block:: bash

    pip install django-i18n-fields[md]

    # Or install martor separately
    pip install django-i18n-fields martor

Install from Git
~~~~~~~~~~~~~~~~

Install the latest development version from GitHub:

.. code-block:: bash

    # Latest stable version
    pip install git+https://github.com/huynguyengl99/django-i18n-fields.git

    # Specific branch or tag
    pip install git+https://github.com/huynguyengl99/django-i18n-fields.git@main

Verify Installation
-------------------

After installation, verify that Django i18n Fields is properly installed:

.. code-block:: python

    # In Python shell or Django shell
    import i18n_fields
    print(i18n_fields.__version__)

    # Check available modules
    from i18n_fields import LocalizedCharField, LocalizedTextField

    # Check Markdown/martor support (if installed)
    from i18n_fields import LocalizedMartorField

    # Check DRF support (if installed)
    from i18n_fields.drf import LocalizedModelSerializer

Next Steps
----------

After installation, proceed to :doc:`getting-started` for configuration and setup instructions.
