Admin Reference
===============

This page documents the Django admin integration components.

LocalizedFieldsAdmin
--------------------

.. class:: LocalizedFieldsAdmin

   Base admin class for models with localized fields. Combines ``LocalizedFieldsAdminMixin`` with ``admin.ModelAdmin``.

   **Usage:**

   .. code-block:: python

       from i18n_fields import LocalizedFieldsAdmin
       from .models import Article

       @admin.register(Article)
       class ArticleAdmin(LocalizedFieldsAdmin):
           list_display = ['title', 'created_at']

   **Features:**

   - All features of ``LocalizedFieldsAdminMixin``
   - No need to explicitly extend ``admin.ModelAdmin``
   - Cleaner, more concise syntax
   - Full type safety with Generic types

   **When to Use:**

   Use ``LocalizedFieldsAdmin`` when you don't need to combine with other admin base classes. For multiple inheritance scenarios, use ``LocalizedFieldsAdminMixin`` instead.

LocalizedFieldsAdminMixin
-------------------------

.. class:: LocalizedFieldsAdminMixin

   Mixin for Django admin that enables localized field widgets and proper display.

   **Usage:**

   .. code-block:: python

       from django.contrib import admin
       from i18n_fields import LocalizedFieldsAdminMixin
       from .models import Article

       @admin.register(Article)
       class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
           list_display = ['title', 'created_at']

   **Features:**

   - Automatic widget selection for localized fields
   - Tab or dropdown language switchers
   - Proper display in list_display
   - Read-only field support
   - Works with inlines

   **Attributes:**

   .. attribute:: localized_fields_display

      Display mode for localized fields: ``"tab"`` or ``"dropdown"``

      **Default:** ``None`` (uses ``I18N_FIELDS["DISPLAY"]`` setting)

      **Example:**

      .. code-block:: python

          class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
              localized_fields_display = 'dropdown'

   **Methods:**

   .. method:: formfield_for_dbfield(db_field, request, **kwargs)

      Override to use localized field widgets.

      **Parameters:**

      - ``db_field``: The database field
      - ``request``: The HTTP request
      - ``**kwargs``: Additional arguments

      **Returns:** Form field with appropriate widget

   .. method:: get_fieldsets(request, obj=None)

      Get fieldsets with localized readonly field names replaced.

      **Parameters:**

      - ``request``: The HTTP request
      - ``obj``: The model instance (None for add view)

      **Returns:** List of fieldsets

   **Class Attributes:**

   .. attribute:: Media

      Media class that includes required CSS and JavaScript files.

      **CSS:**

      - ``i18n_fields/i18n-fields-admin.css``

      **JavaScript:**

      - ``admin/js/jquery.init.js``
      - ``i18n_fields/i18n-fields-admin.js``

Display Modes
-------------

Tab Mode
~~~~~~~~

Shows language tabs above each field.

**Configuration:**

.. code-block:: python

    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        localized_fields_display = 'tab'

**Features:**

- Horizontal tabs for each language
- Active tab highlighted
- Easy switching between languages
- Best for 2-6 languages

**Visual Structure:**

.. code-block:: text

    ┌─────────┬─────────┬─────────┐
    │ English │ Spanish │ French  │  ← Tabs
    └─────────┴─────────┴─────────┘
    ┌─────────────────────────────┐
    │ Field content in English... │  ← Content
    └─────────────────────────────┘

Dropdown Mode
~~~~~~~~~~~~~

Shows a dropdown menu to select language.

**Configuration:**

.. code-block:: python

    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        localized_fields_display = 'dropdown'

**Features:**

- Dropdown with all languages
- More compact
- Good for 7+ languages

**Visual Structure:**

.. code-block:: text

    ┌──────────────────────┐
    │ English        ▼    │  ← Dropdown
    └──────────────────────┘
    ┌─────────────────────────────┐
    │ Field content in English... │  ← Content
    └─────────────────────────────┘

Widgets
-------

AdminLocalizedFieldWidget
~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: AdminLocalizedFieldWidget(display_mode='tab')

   Base widget for localized fields in admin.

   **Parameters:**

   - ``display_mode`` (str): ``"tab"`` or ``"dropdown"``

   **Used For:** Base ``LocalizedField``

AdminLocalizedCharFieldWidget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: AdminLocalizedCharFieldWidget(display_mode='tab')

   Widget for ``LocalizedCharField`` with text input.

   **Inherits From:** ``AdminLocalizedFieldWidget``

   **HTML Input:** ``<input type="text">``

AdminLocalizedIntegerFieldWidget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: AdminLocalizedIntegerFieldWidget(display_mode='tab')

   Widget for ``LocalizedIntegerField`` with number input.

   **HTML Input:** ``<input type="number">``

AdminLocalizedFloatFieldWidget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: AdminLocalizedFloatFieldWidget(display_mode='tab')

   Widget for ``LocalizedFloatField`` with number input.

   **HTML Input:** ``<input type="number" step="any">``

AdminLocalizedBooleanFieldWidget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: AdminLocalizedBooleanFieldWidget(display_mode='tab')

   Widget for ``LocalizedBooleanField`` with checkbox.

   **HTML Input:** ``<input type="checkbox">``

AdminLocalizedFileFieldWidget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: AdminLocalizedFileFieldWidget(display_mode='tab')

   Widget for ``LocalizedFileField`` with file input.

   **HTML Input:** ``<input type="file">``

   **Features:**

   - Shows current file
   - Clear checkbox
   - Upload new file

List Display
------------

Localized fields in ``list_display`` automatically show translated values.

**Example:**

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        list_display = ['title', 'author', 'created_at']

**Behavior:**

- Shows value in active language
- Falls back to primary language if active language unavailable
- Shows "-" if no value available

**Custom Display:**

.. code-block:: python

    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        list_display = ['custom_title', 'created_at']

        def custom_title(self, obj):
            return f"{obj.title} (ID: {obj.id})"
        custom_title.short_description = 'Title'

Readonly Fields
---------------

Read-only localized fields show all translations.

**Example:**

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        readonly_fields = ['slug', 'created_at']
        fields = ['title', 'slug', 'content', 'created_at']

**Behavior:**

- Shows tab or dropdown interface (based on ``localized_fields_display``)
- All translations visible but not editable
- Respects display mode setting

Inline Admin
------------

Use with inline admin classes:

**TabularInline:**

.. code-block:: python

    class ChapterInline(LocalizedFieldsAdminMixin, admin.TabularInline):
        model = Chapter
        fields = ['title', 'order']
        extra = 1

    @admin.register(Book)
    class BookAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        inlines = [ChapterInline]

**StackedInline:**

.. code-block:: python

    class ChapterInline(LocalizedFieldsAdminMixin, admin.StackedInline):
        model = Chapter
        fields = ['title', 'content', 'order']
        extra = 0

**Behavior:**

- Each inline row has localized field widgets
- Same display mode as parent admin
- Works with TabularInline and StackedInline

Fieldsets
---------

Organize localized fields in fieldsets:

**Example:**

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        fieldsets = [
            ('Content', {
                'fields': ['title', 'slug', 'content']
            }),
            ('Metadata', {
                'fields': ['author', 'published', 'created_at'],
                'classes': ['collapse']
            }),
        ]

**Features:**

- Localized fields work in any fieldset
- Support for ``classes`` (e.g., ``collapse``, ``wide``)
- Support for ``description``

Search
------

Enable search by specific languages:

**Example:**

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        search_fields = [
            'title__en',
            'title__es',
            'content__en',
            'author__name',
        ]

**Usage:**

.. code-block:: python

    # Search across English and Spanish titles
    # Admin search box will search all specified fields

Filtering
---------

Custom Filters
~~~~~~~~~~~~~~

Create custom filters for localized fields:

.. code-block:: python

    from django.contrib import admin

    class TitleLanguageFilter(admin.SimpleListFilter):
        title = 'title language availability'
        parameter_name = 'title_lang'

        def lookups(self, request, model_admin):
            return [
                ('en', 'Has English'),
                ('es', 'Has Spanish'),
                ('fr', 'Has French'),
            ]

        def queryset(self, request, queryset):
            if self.value() == 'en':
                return queryset.filter(title__en__isnull=False)
            if self.value() == 'es':
                return queryset.filter(title__es__isnull=False)
            if self.value() == 'fr':
                return queryset.filter(title__fr__isnull=False)

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        list_filter = [TitleLanguageFilter, 'published']

Ordering
--------

Order by localized fields:

**Example:**

.. code-block:: python

    from i18n_fields import L

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        def get_queryset(self, request):
            qs = super().get_queryset(request)
            # Order by title in current language
            return qs.order_by(L('title'))

        # Alternative: Order by specific language
        def get_queryset(self, request):
            qs = super().get_queryset(request)
            return qs.order_by(L('title', 'en'))

Actions
-------

Admin actions work with localized fields:

**Example:**

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        actions = ['duplicate_to_spanish']

        def duplicate_to_spanish(self, request, queryset):
            for article in queryset:
                title = article.title
                if title.get('en') and not title.get('es'):
                    # Copy English to Spanish
                    title.set('es', title.get('en'))
                    article.title = title
                    article.save()

            self.message_user(
                request,
                f'{queryset.count()} articles updated'
            )
        duplicate_to_spanish.short_description = 'Duplicate EN to ES'

Customization
-------------

Custom Widgets
~~~~~~~~~~~~~~

Override widgets for specific fields:

.. code-block:: python

    from i18n_fields.widgets import AdminLocalizedFieldWidget

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        def formfield_for_dbfield(self, db_field, request, **kwargs):
            if db_field.name == 'title':
                kwargs['widget'] = AdminLocalizedFieldWidget(
                    display_mode='dropdown'
                )
            return super().formfield_for_dbfield(db_field, request, **kwargs)

Custom CSS
~~~~~~~~~~

Add custom styling:

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        class Media:
            css = {
                'all': ('css/custom_i18n_admin.css',)
            }

.. code-block:: css

    /* static/css/custom_i18n_admin.css */
    .i18n-tab {
        padding: 10px 20px;
        font-weight: bold;
    }

    .i18n-tab.active {
        background-color: #0066cc;
        color: white;
    }

Best Practices
--------------

1. **Use LocalizedFieldsAdmin or LocalizedFieldsAdminMixin**

   Always use one of these for proper widget support:

   .. code-block:: python

       # Best - using base class
       class ArticleAdmin(LocalizedFieldsAdmin):
           pass

       # Good - using mixin
       class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
           pass

       # Missing features - don't do this
       class ArticleAdmin(admin.ModelAdmin):
           pass

2. **Choose Appropriate Display Mode**

   - **Tab mode**: Best for 2-6 languages
   - **Dropdown mode**: Best for 7+ languages

3. **Include in list_display**

   Show localized fields in list view:

   .. code-block:: python

       list_display = ['title', 'created_at', 'published']

4. **Use Language-Specific Search**

   Specify languages in search_fields:

   .. code-block:: python

       search_fields = ['title__en', 'title__es', 'content__en']

5. **Order Explicitly**

   Use ``L()`` for consistent ordering:

   .. code-block:: python

       def get_queryset(self, request):
           return super().get_queryset(request).order_by(L('title', 'en'))

Troubleshooting
---------------

Widgets Not Showing
~~~~~~~~~~~~~~~~~~~

**Problem:** Localized field widgets not appearing

**Solution:**

1. Ensure mixin is included and comes first:

   .. code-block:: python

       class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
           pass

2. Check static files are collected:

   .. code-block:: bash

       python manage.py collectstatic

JavaScript Not Working
~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Tabs/dropdowns not switching

**Solution:**

1. Check browser console for errors
2. Ensure jQuery is loaded (required by Django admin)
3. Clear browser cache

Readonly Fields Not Displaying
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Readonly localized fields showing as plain text

**Solution:**

Ensure the mixin is included - it handles readonly field display automatically.

See Also
--------

- :doc:`../user-guides/admin-integration` - Admin integration guide
- :doc:`fields` - Localized field types
- `Django Admin <https://docs.djangoproject.com/en/stable/ref/contrib/admin/>`_
