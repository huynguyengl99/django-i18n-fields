Django Admin Integration
========================

Django i18n Fields provides comprehensive Django admin support with beautiful tab and dropdown interfaces for managing multilingual content.

Quick Setup
-----------

Basic Admin Integration
~~~~~~~~~~~~~~~~~~~~~~~~

There are two ways to enable localized field widgets in Django admin:

**Option 1: Using LocalizedFieldsAdmin (Recommended)**

Use the ``LocalizedFieldsAdmin`` base class for the simplest setup:

.. code-block:: python

    # admin.py
    from i18n_fields import LocalizedFieldsAdmin
    from .models import Article

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdmin):
        list_display = ['title', 'created_at']
        fields = ['title', 'content', 'published']

**Option 2: Using LocalizedFieldsAdminMixin**

Use the mixin when you need to combine with other base classes:

.. code-block:: python

    # admin.py
    from django.contrib import admin
    from i18n_fields import LocalizedFieldsAdminMixin
    from .models import Article

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        list_display = ['title', 'created_at']
        fields = ['title', 'content', 'published']

That's it! All localized fields will automatically get tab/dropdown widgets.

Display Modes
-------------

Tab Mode (Default)
~~~~~~~~~~~~~~~~~~

Shows language tabs above each localized field:

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        localized_fields_display = 'tab'  # or omit (tab is default)

**Features:**
- Tabs for each configured language
- Active tab highlighted
- Easy switching between languages
- Best for 2-6 languages

Dropdown Mode
~~~~~~~~~~~~~

Shows a dropdown menu to select the language:

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        localized_fields_display = 'dropdown'

**Features:**
- Dropdown menu with language names
- More compact for many languages
- Good for 7+ languages

Global Configuration
~~~~~~~~~~~~~~~~~~~~

Set the default display mode in settings:

.. code-block:: python

    # settings.py
    I18N_FIELDS = {
        "DISPLAY": "dropdown",  # or "tab"
    }

List Display
------------

Localized fields work seamlessly in list_display:

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        list_display = ['title', 'author', 'created_at', 'published']
        list_filter = ['published', 'created_at']
        search_fields = ['title__en', 'title__es']

The mixin automatically shows translated values in the current language.

Readonly Fields
---------------

Read-only localized fields display all translations:

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        readonly_fields = ['slug', 'created_at']
        fields = ['title', 'slug', 'content', 'created_at']

Read-only fields show a tab/dropdown interface with all translations visible but not editable.

Fieldsets
---------

Organize localized fields in fieldsets:

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        fieldsets = [
            ('Basic Information', {
                'fields': ['title', 'slug', 'author']
            }),
            ('Content', {
                'fields': ['content', 'excerpt'],
                'classes': ['wide']
            }),
            ('Metadata', {
                'fields': ['published', 'created_at'],
                'classes': ['collapse']
            }),
        ]

Inline Admin
------------

Localized fields work in inline admin:

.. code-block:: python

    class ChapterInline(LocalizedFieldsAdminMixin, admin.TabularInline):
        model = Chapter
        fields = ['title', 'order']
        extra = 1

    @admin.register(Book)
    class BookAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        inlines = [ChapterInline]

Search
------

Enable search by specific languages:

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        search_fields = [
            'title__en',      # Search English titles
            'title__es',      # Search Spanish titles
            'content__en',    # Search English content
            'author__name',   # Regular field
        ]

Filtering
---------

Filter by localized field values:

.. code-block:: python

    from django.contrib import admin
    from i18n_fields import LocalizedFieldsAdminMixin

    class PublishedFilter(admin.SimpleListFilter):
        title = 'published status'
        parameter_name = 'published'

        def lookups(self, request, model_admin):
            return [
                ('yes', 'Published'),
                ('no', 'Not Published'),
            ]

        def queryset(self, request, queryset):
            if self.value() == 'yes':
                return queryset.filter(published=True)
            if self.value() == 'no':
                return queryset.filter(published=False)

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        list_filter = [PublishedFilter, 'created_at']

Ordering
--------

Order by localized fields in admin:

.. code-block:: python

    from i18n_fields import L

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        def get_queryset(self, request):
            qs = super().get_queryset(request)
            # Order by title in current language
            return qs.order_by(L('title'))

Custom Widgets
--------------

Override widgets for specific fields:

.. code-block:: python

    from django import forms
    from i18n_fields.widgets import AdminLocalizedFieldWidget

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        def formfield_for_dbfield(self, db_field, request, **kwargs):
            if db_field.name == 'title':
                kwargs['widget'] = AdminLocalizedFieldWidget(
                    display_mode='dropdown'
                )
            return super().formfield_for_dbfield(db_field, request, **kwargs)

Form Validation
---------------

Custom validation works normally:

.. code-block:: python

    from django import forms

    class ArticleAdminForm(forms.ModelForm):
        class Meta:
            model = Article
            fields = '__all__'

        def clean_title(self):
            title = self.cleaned_data['title']
            # Validate English title exists
            if not title.get('en'):
                raise forms.ValidationError('English title is required')
            return title

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        form = ArticleAdminForm

Actions
-------

Admin actions work with localized fields:

.. code-block:: python

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        actions = ['publish_articles', 'duplicate_to_spanish']

        def publish_articles(self, request, queryset):
            queryset.update(published=True)
            self.message_user(request, f'{queryset.count()} articles published')

        def duplicate_to_spanish(self, request, queryset):
            for article in queryset:
                # Copy English to Spanish
                title = article.title
                if title.get('en') and not title.get('es'):
                    title.set('es', title.get('en'))
                    article.title = title
                    article.save()
            self.message_user(request, 'Duplicated to Spanish')

Complete Example
----------------

Here's a comprehensive example:

.. code-block:: python

    # admin.py
    from django.contrib import admin
    from django.utils.html import format_html
    from i18n_fields import LocalizedFieldsAdmin, L
    from .models import Article, Category

    class CategoryInline(admin.TabularInline):
        model = Article.categories.through
        extra = 1

    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdmin):
        # Display mode
        localized_fields_display = 'tab'

        # List display
        list_display = [
            'title',
            'author',
            'published_status',
            'created_at'
        ]
        list_filter = ['published', 'created_at', 'author']
        search_fields = ['title__en', 'title__es', 'content__en']

        # Fieldsets
        fieldsets = [
            ('Content', {
                'fields': ['title', 'slug', 'content', 'excerpt']
            }),
            ('Metadata', {
                'fields': ['author', 'published', 'created_at', 'updated_at'],
                'classes': ['collapse']
            }),
        ]

        readonly_fields = ['slug', 'created_at', 'updated_at']
        inlines = [CategoryInline]

        # Custom methods
        def published_status(self, obj):
            if obj.published:
                return format_html(
                    '<span style="color: green;">✓ Published</span>'
                )
            return format_html(
                '<span style="color: red;">✗ Draft</span>'
            )
        published_status.short_description = 'Status'

        def get_queryset(self, request):
            qs = super().get_queryset(request)
            return qs.select_related('author').order_by(L('title'))

Styling
-------

The admin widgets come with default styles, but you can customize them:

.. code-block:: python

    # admin.py
    @admin.register(Article)
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        class Media:
            css = {
                'all': ('css/custom_admin.css',)
            }

.. code-block:: css

    /* static/css/custom_admin.css */
    .i18n-tabs {
        background-color: #f0f0f0;
        border-radius: 5px;
    }

    .i18n-tab.active {
        background-color: #0066cc;
        color: white;
    }

Best Practices
--------------

1. **Use LocalizedFieldsAdmin or LocalizedFieldsAdminMixin**

   Always use one of these for localized fields:

   .. code-block:: python

       # Best - using base class (recommended)
       class ArticleAdmin(LocalizedFieldsAdmin):
           pass

       # Good - using mixin
       class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
           pass

       # Missing features without them
       class ArticleAdmin(admin.ModelAdmin):
           pass

2. **Configure list_display**

   Include localized fields in list_display to show translated content:

   .. code-block:: python

       list_display = ['title', 'created_at']  # Shows translated title

3. **Search by Language**

   Specify languages in search_fields for better search:

   .. code-block:: python

       search_fields = ['title__en', 'title__es', 'content__en']

4. **Choose Appropriate Display Mode**

   - Use **tab mode** for 2-6 languages
   - Use **dropdown mode** for 7+ languages

5. **Order Appropriately**

   Use ``L()`` expression for ordering in the current language:

   .. code-block:: python

       def get_queryset(self, request):
           return super().get_queryset(request).order_by(L('title'))

Troubleshooting
---------------

**Widgets Not Showing**

Make sure ``LocalizedFieldsAdminMixin`` is included and comes before ``admin.ModelAdmin``:

.. code-block:: python

    # Correct
    class ArticleAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
        pass

**Static Files Not Loading**

Run collectstatic:

.. code-block:: bash

    python manage.py collectstatic

**Tabs Not Switching**

Check browser console for JavaScript errors. Ensure jQuery is loaded.

Next Steps
----------

- :doc:`drf-integration` - Integrate with Django REST Framework
- :doc:`advanced-queries` - Advanced querying techniques
- :doc:`../reference/admin` - Complete admin reference
