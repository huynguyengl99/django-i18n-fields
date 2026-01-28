Django REST Framework Integration
===================================

Django i18n Fields provides first-class Django REST Framework (DRF) support with automatic serialization in the active language.

Quick Setup
-----------

Basic Serializer
~~~~~~~~~~~~~~~~

Use ``LocalizedModelSerializer`` for automatic handling of localized fields:

.. code-block:: python

    # serializers.py
    from i18n_fields.drf import LocalizedModelSerializer
    from .models import Article

    class ArticleSerializer(LocalizedModelSerializer):
        class Meta:
            model = Article
            fields = ['id', 'title', 'content', 'created_at']

**Output** (with English active):

.. code-block:: json

    {
        "id": 1,
        "title": "Hello World",
        "content": "This is the content.",
        "created_at": "2025-01-28T10:00:00Z"
    }

How It Works
------------

Automatic Translation
~~~~~~~~~~~~~~~~~~~~~

``LocalizedModelSerializer`` automatically:

1. Serializes localized fields to simple values (not dicts)
2. Uses the active language from Django's translation system
3. Handles all localized field types correctly
4. Supports DRF Spectacular for API documentation

.. code-block:: python

    # With active language set to Spanish
    from django.utils import translation

    with translation.override('es'):
        serializer = ArticleSerializer(article)
        print(serializer.data['title'])  # "Hola Mundo"

Field Mapping
~~~~~~~~~~~~~

The serializer maps localized fields to appropriate DRF fields:

- ``LocalizedCharField`` → ``CharField``
- ``LocalizedTextField`` → ``CharField``
- ``LocalizedIntegerField`` → ``IntegerField``
- ``LocalizedFloatField`` → ``FloatField``
- ``LocalizedBooleanField`` → ``BooleanField``
- ``LocalizedFileField`` → ``FileField``
- ``LocalizedUniqueSlugField`` → ``SlugField``

ViewSets
--------

Basic ViewSet
~~~~~~~~~~~~~

Use with any DRF viewset:

.. code-block:: python

    # views.py
    from rest_framework import viewsets
    from .models import Article
    from .serializers import ArticleSerializer

    class ArticleViewSet(viewsets.ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSerializer

Language Negotiation
~~~~~~~~~~~~~~~~~~~~

Use Django's language negotiation with the Accept-Language header:

.. code-block:: python

    # views.py
    from rest_framework import viewsets
    from django.utils import translation

    class ArticleViewSet(viewsets.ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSerializer

        def get_serializer_context(self):
            context = super().get_serializer_context()
            # Language is already set from middleware
            context['language'] = translation.get_language()
            return context

**API Request Example:**

.. code-block:: bash

    curl -H "Accept-Language: es" http://api.example.com/articles/1/

**Response:**

.. code-block:: json

    {
        "id": 1,
        "title": "Hola Mundo",
        "content": "Este es el contenido."
    }

Creating Objects
----------------

Simple Input
~~~~~~~~~~~~

Send translations as a dictionary:

.. code-block:: python

    # POST /api/articles/
    {
        "title": {
            "en": "Hello World",
            "es": "Hola Mundo"
        },
        "content": {
            "en": "Content in English",
            "es": "Contenido en español"
        }
    }

The serializer automatically converts dictionaries to ``LocalizedValue`` objects.

Single Language Input
~~~~~~~~~~~~~~~~~~~~~

Send a string to set only the active language:

.. code-block:: python

    # POST /api/articles/ (with Accept-Language: en)
    {
        "title": "Hello World",
        "content": "Content in English"
    }

This sets values only for English.

Partial Updates
~~~~~~~~~~~~~~~

Update specific languages:

.. code-block:: python

    # PATCH /api/articles/1/
    {
        "title": {
            "es": "Nuevo Título"  # Only update Spanish
        }
    }

Custom Serializers
------------------

Field-Level Customization
~~~~~~~~~~~~~~~~~~~~~~~~~

Override specific fields:

.. code-block:: python

    from rest_framework import serializers
    from i18n_fields.drf import LocalizedModelSerializer

    class ArticleSerializer(LocalizedModelSerializer):
        # Custom read-only field
        summary = serializers.SerializerMethodField()

        class Meta:
            model = Article
            fields = ['id', 'title', 'content', 'summary']

        def get_summary(self, obj):
            # Returns translated content
            return obj.content.translate()[:100]

Full Translation Output
~~~~~~~~~~~~~~~~~~~~~~~

Return all translations in the response:

.. code-block:: python

    from rest_framework import serializers
    from i18n_fields.drf import LocalizedModelSerializer

    class ArticleDetailSerializer(LocalizedModelSerializer):
        all_translations = serializers.SerializerMethodField()

        class Meta:
            model = Article
            fields = ['id', 'title', 'content', 'all_translations']

        def get_all_translations(self, obj):
            return {
                'title': dict(obj.title),
                'content': dict(obj.content)
            }

**Output:**

.. code-block:: json

    {
        "id": 1,
        "title": "Hello World",
        "content": "Content in English",
        "all_translations": {
            "title": {
                "en": "Hello World",
                "es": "Hola Mundo",
                "fr": "Bonjour le Monde"
            },
            "content": {
                "en": "Content in English",
                "es": "Contenido en español"
            }
        }
    }

Nested Serializers
------------------

Localized fields work in nested serializers:

.. code-block:: python

    class AuthorSerializer(LocalizedModelSerializer):
        class Meta:
            model = Author
            fields = ['id', 'name', 'bio']

    class ArticleSerializer(LocalizedModelSerializer):
        author = AuthorSerializer(read_only=True)

        class Meta:
            model = Article
            fields = ['id', 'title', 'content', 'author']

**Output:**

.. code-block:: json

    {
        "id": 1,
        "title": "Hello World",
        "content": "Content",
        "author": {
            "id": 1,
            "name": "John Doe",
            "bio": "Author bio in English"
        }
    }

Filtering
---------

Filter by Language
~~~~~~~~~~~~~~~~~~

Use query parameters to filter by specific languages:

.. code-block:: python

    from rest_framework import viewsets
    from django_filters import rest_framework as filters

    class ArticleFilter(filters.FilterSet):
        title_en = filters.CharFilter(field_name='title__en', lookup_expr='icontains')
        title_es = filters.CharFilter(field_name='title__es', lookup_expr='icontains')

        class Meta:
            model = Article
            fields = ['title_en', 'title_es']

    class ArticleViewSet(viewsets.ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSerializer
        filterset_class = ArticleFilter

**Usage:**

.. code-block:: bash

    # Filter by English title
    GET /api/articles/?title_en=hello

    # Filter by Spanish title
    GET /api/articles/?title_es=hola

Ordering
--------

Order by Localized Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from rest_framework import viewsets
    from i18n_fields import L

    class ArticleViewSet(viewsets.ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSerializer

        def get_queryset(self):
            queryset = super().get_queryset()
            # Order by title in current language
            return queryset.order_by(L('title'))

DRF Spectacular Integration
----------------------------

Automatic Schema Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Django i18n Fields works seamlessly with DRF Spectacular:

.. code-block:: python

    # settings.py
    INSTALLED_APPS = [
        # ...
        'drf_spectacular',
        'i18n_fields',
    ]

    REST_FRAMEWORK = {
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    }

    SPECTACULAR_SETTINGS = {
        'TITLE': 'Your API',
        'VERSION': '1.0.0',
    }

The schema will show localized fields as simple types (string, integer, etc.) in the active language.

Custom Schema
~~~~~~~~~~~~~

Customize the schema for localized fields:

.. code-block:: python

    from drf_spectacular.utils import extend_schema_field
    from rest_framework import serializers

    class ArticleSerializer(LocalizedModelSerializer):
        @extend_schema_field(serializers.CharField)
        title = serializers.CharField()

        class Meta:
            model = Article
            fields = ['id', 'title', 'content']

Pagination
----------

Localized fields work with pagination:

.. code-block:: python

    from rest_framework.pagination import PageNumberPagination

    class ArticlePagination(PageNumberPagination):
        page_size = 10

    class ArticleViewSet(viewsets.ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSerializer
        pagination_class = ArticlePagination

Search
------

Search Across Languages
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from rest_framework import filters

    class ArticleViewSet(viewsets.ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSerializer
        filter_backends = [filters.SearchFilter]
        search_fields = ['title__en', 'title__es', 'content__en']

**Usage:**

.. code-block:: bash

    GET /api/articles/?search=hello

Permissions
-----------

Permissions work normally with localized fields:

.. code-block:: python

    from rest_framework import permissions

    class IsAuthorOrReadOnly(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.author == request.user

    class ArticleViewSet(viewsets.ModelViewSet):
        queryset = Article.objects.all()
        serializer_class = ArticleSerializer
        permission_classes = [IsAuthorOrReadOnly]

Complete Example
----------------

Here's a full example with all features:

.. code-block:: python

    # serializers.py
    from rest_framework import serializers
    from i18n_fields.drf import LocalizedModelSerializer
    from .models import Article, Category

    class CategorySerializer(LocalizedModelSerializer):
        class Meta:
            model = Category
            fields = ['id', 'name']

    class ArticleListSerializer(LocalizedModelSerializer):
        category = CategorySerializer(read_only=True)
        author_name = serializers.CharField(source='author.name', read_only=True)

        class Meta:
            model = Article
            fields = ['id', 'title', 'category', 'author_name', 'created_at']

    class ArticleDetailSerializer(LocalizedModelSerializer):
        category = CategorySerializer(read_only=True)
        all_translations = serializers.SerializerMethodField()

        class Meta:
            model = Article
            fields = [
                'id', 'title', 'content', 'category',
                'author', 'created_at', 'all_translations'
            ]

        def get_all_translations(self, obj):
            return {
                'title': dict(obj.title),
                'content': dict(obj.content),
            }

    # views.py
    from rest_framework import viewsets, filters
    from django_filters import rest_framework as django_filters
    from i18n_fields import L
    from .models import Article
    from .serializers import ArticleListSerializer, ArticleDetailSerializer

    class ArticleFilter(django_filters.FilterSet):
        title = django_filters.CharFilter(field_name='title__en', lookup_expr='icontains')

        class Meta:
            model = Article
            fields = ['category', 'author']

    class ArticleViewSet(viewsets.ModelViewSet):
        queryset = Article.objects.select_related('author', 'category')
        filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
        filterset_class = ArticleFilter
        search_fields = ['title__en', 'title__es', 'content__en']
        ordering_fields = ['created_at']

        def get_serializer_class(self):
            if self.action == 'list':
                return ArticleListSerializer
            return ArticleDetailSerializer

        def get_queryset(self):
            queryset = super().get_queryset()
            return queryset.order_by(L('title'))

    # urls.py
    from rest_framework.routers import DefaultRouter
    from .views import ArticleViewSet

    router = DefaultRouter()
    router.register(r'articles', ArticleViewSet)

    urlpatterns = router.urls

Best Practices
--------------

1. **Use LocalizedModelSerializer**

   Always use the specialized serializer for models with localized fields:

   .. code-block:: python

       # Good
       class ArticleSerializer(LocalizedModelSerializer):
           pass

       # Missing automatic translation
       class ArticleSerializer(serializers.ModelSerializer):
           pass

2. **Language Negotiation**

   Use Django's middleware for automatic language detection:

   .. code-block:: python

       MIDDLEWARE = [
           # ...
           'django.middleware.locale.LocaleMiddleware',
       ]

3. **Return All Translations for Admin**

   Provide endpoints that return all translations for admin interfaces:

   .. code-block:: python

       class ArticleAdminSerializer(LocalizedModelSerializer):
           translations = serializers.SerializerMethodField()

           def get_translations(self, obj):
               return {'title': dict(obj.title)}

4. **Validate Required Languages**

   Add custom validation for required languages:

   .. code-block:: python

       def validate_title(self, value):
           if not value.get('en'):
               raise serializers.ValidationError('English title required')
           return value

5. **Use Filtering and Search**

   Enable filtering by specific languages for better search:

   .. code-block:: python

       search_fields = ['title__en', 'title__es', 'content__en']

Troubleshooting
---------------

**Serializer Not Translating**

Ensure you're using ``LocalizedModelSerializer``:

.. code-block:: python

    from i18n_fields.drf import LocalizedModelSerializer

**Wrong Language Returned**

Check the active language:

.. code-block:: python

    from django.utils import translation
    print(translation.get_language())

**DRF Not Installed**

Install Django REST Framework:

.. code-block:: bash

    pip install djangorestframework

Next Steps
----------

- :doc:`advanced-queries` - Advanced querying techniques
- :doc:`../reference/fields` - Complete field reference
- `DRF Documentation <https://www.django-rest-framework.org/>`_
