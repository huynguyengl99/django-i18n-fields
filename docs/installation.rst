Installation
============

Dependencies
------------

Django i18n Fields has minimal dependencies:

**Core Dependencies**:

- **Django** (>=5.0) - Web framework with JSONField support
- **Python** (>=3.10) - Modern Python version

**Optional Dependencies**:

- **Django REST Framework** (>=3.0) - For REST API integration
- **DRF Spectacular** - For automatic API documentation generation

Installation Options
--------------------

Basic Installation
~~~~~~~~~~~~~~~~~~

Install Django i18n Fields using pip:

.. code-block:: bash

    pip install django-i18n-fields

With Django REST Framework Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're using Django REST Framework:

.. code-block:: bash

    pip install django-i18n-fields djangorestframework

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

    # Check DRF support (if installed)
    from i18n_fields.drf import LocalizedModelSerializer

Next Steps
----------

After installation, proceed to :doc:`getting-started` for configuration and setup instructions.
