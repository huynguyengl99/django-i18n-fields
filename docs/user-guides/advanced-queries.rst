Advanced Queries
================

This guide covers advanced querying techniques for localized fields including filtering, ordering, annotations, and aggregations.

Query Expressions
-----------------

L() - Localized Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~

``L()`` is a shorthand function for creating localized references in queries:

.. code-block:: python

    from i18n_fields import L

    # Order by current language
    articles = Article.objects.order_by(L('title'))

    # Order by specific language
    articles = Article.objects.order_by(L('title', 'en'))

    # Descending order
    articles = Article.objects.order_by(L('title').desc())

    # Multiple fields
    articles = Article.objects.order_by(L('category'), L('title'))

LocalizedRef
~~~~~~~~~~~~

``LocalizedRef`` is the full class behind ``L()``:

.. code-block:: python

    from i18n_fields import LocalizedRef

    # Equivalent to L('title')
    ref = LocalizedRef('title')

    # With specific language
    ref = LocalizedRef('title', 'en')

Use ``LocalizedRef`` for more complex queries:

.. code-block:: python

    from django.db.models import Q
    from i18n_fields import LocalizedRef

    # Complex filtering
    articles = Article.objects.filter(
        Q(published=True) &
        Q(**{LocalizedRef('title', 'en'): 'Hello'})
    )

Filtering
---------

By Specific Language
~~~~~~~~~~~~~~~~~~~~

Filter using JSON field lookups:

.. code-block:: python

    # Exact match
    articles = Article.objects.filter(title__en='Hello World')

    # Case-insensitive
    articles = Article.objects.filter(title__en__iexact='hello world')

    # Contains
    articles = Article.objects.filter(title__en__icontains='hello')

    # Starts with
    articles = Article.objects.filter(title__en__istartswith='hello')

    # Ends with
    articles = Article.objects.filter(title__en__iendswith='world')

Multiple Languages
~~~~~~~~~~~~~~~~~~

Filter by multiple languages:

.. code-block:: python

    # Articles with both English and Spanish titles
    articles = Article.objects.filter(
        title__en__isnull=False,
        title__es__isnull=False
    )

    # Articles where English and Spanish match
    articles = Article.objects.filter(
        title__en='Hello',
        title__es='Hola'
    )

Null Checks
~~~~~~~~~~~

Check for missing translations:

.. code-block:: python

    # Articles without Spanish translation
    articles = Article.objects.filter(title__es__isnull=True)

    # Articles with Spanish translation
    articles = Article.objects.filter(title__es__isnull=False)

    # Articles with any translation
    articles = Article.objects.exclude(title__isnull=True)

Complex Queries
~~~~~~~~~~~~~~~

Combine multiple conditions:

.. code-block:: python

    from django.db.models import Q

    # English OR Spanish title contains "world"
    articles = Article.objects.filter(
        Q(title__en__icontains='world') |
        Q(title__es__icontains='mundo')
    )

    # Published AND has English title
    articles = Article.objects.filter(
        Q(published=True) &
        Q(title__en__isnull=False)
    )

Ordering
--------

By Current Language
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from i18n_fields import L

    # Ascending
    articles = Article.objects.order_by(L('title'))

    # Descending
    articles = Article.objects.order_by(L('title').desc())

    # Multiple fields
    articles = Article.objects.order_by(L('category'), L('title'))

By Specific Language
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Order by English title
    articles = Article.objects.order_by(L('title', 'en'))

    # Order by Spanish title
    articles = Article.objects.order_by(L('title', 'es'))

    # Multiple languages
    articles = Article.objects.order_by(
        L('title', 'en'),
        L('title', 'es')
    )

Mixed Ordering
~~~~~~~~~~~~~~

Combine localized and regular fields:

.. code-block:: python

    from i18n_fields import L

    # Order by date, then by title
    articles = Article.objects.order_by('-created_at', L('title'))

    # Order by category, then by title in Spanish
    articles = Article.objects.order_by('category', L('title', 'es'))

Annotations
-----------

Basic Annotations
~~~~~~~~~~~~~~~~~

Add localized values to query results:

.. code-block:: python

    from i18n_fields import LocalizedRef

    # Annotate with current language
    articles = Article.objects.annotate(
        title_text=LocalizedRef('title')
    )

    for article in articles:
        print(article.title_text)  # Direct access

Specific Language Annotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Annotate with multiple languages
    articles = Article.objects.annotate(
        title_en=LocalizedRef('title', 'en'),
        title_es=LocalizedRef('title', 'es'),
        title_fr=LocalizedRef('title', 'fr')
    )

    for article in articles:
        print(f"EN: {article.title_en}")
        print(f"ES: {article.title_es}")
        print(f"FR: {article.title_fr}")

Computed Annotations
~~~~~~~~~~~~~~~~~~~~

Use annotations with other query operations:

.. code-block:: python

    from django.db.models import Value, CharField
    from django.db.models.functions import Concat
    from i18n_fields import LocalizedRef

    # Concatenate localized title with suffix
    articles = Article.objects.annotate(
        full_title=Concat(
            LocalizedRef('title', 'en'),
            Value(' - Article'),
            output_field=CharField()
        )
    )

Values and Values List
----------------------

With values()
~~~~~~~~~~~~~

.. code-block:: python

    from i18n_fields import L

    # Get dictionary of values
    data = Article.objects.values(
        'id',
        'created_at',
        title=L('title', 'en')
    )

    # Result: [{'id': 1, 'created_at': ..., 'title': 'Hello'}]

With values_list()
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Get tuples
    titles = Article.objects.values_list(
        L('title', 'en'),
        flat=True
    )

    # Result: ['Hello', 'World', ...]

Multiple Languages
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Get multiple languages
    data = Article.objects.values(
        'id',
        title_en=L('title', 'en'),
        title_es=L('title', 'es')
    )

    # Result: [
    #     {'id': 1, 'title_en': 'Hello', 'title_es': 'Hola'},
    #     ...
    # ]

Aggregations
------------

Count
~~~~~

.. code-block:: python

    from django.db.models import Count

    # Count articles with English title
    count = Article.objects.filter(
        title__en__isnull=False
    ).count()

    # Count by category with English title
    stats = Article.objects.filter(
        title__en__isnull=False
    ).values('category').annotate(
        count=Count('id')
    )

Group By
~~~~~~~~

.. code-block:: python

    from django.db.models import Count
    from i18n_fields import LocalizedRef

    # Group by first letter of title
    from django.db.models.functions import Left

    stats = Article.objects.annotate(
        title_text=LocalizedRef('title', 'en'),
        first_letter=Left('title_text', 1)
    ).values('first_letter').annotate(
        count=Count('id')
    )

Exists Queries
--------------

Subqueries with Exists
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.db.models import Exists, OuterRef

    # Categories with articles having English titles
    categories = Category.objects.annotate(
        has_english_articles=Exists(
            Article.objects.filter(
                category=OuterRef('pk'),
                title__en__isnull=False
            )
        )
    ).filter(has_english_articles=True)

Related Lookups
---------------

Forward Relations
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Filter articles by author's localized name
    articles = Article.objects.filter(
        author__name__en='John Doe'
    )

    # Order by author name
    articles = Article.objects.order_by(L('author__name'))

Reverse Relations
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Authors with articles containing specific English title
    authors = Author.objects.filter(
        articles__title__en__icontains='django'
    ).distinct()

Prefetch and Select Related
----------------------------

Optimize Queries
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Select related with localized fields
    articles = Article.objects.select_related(
        'author',
        'category'
    )

    # Prefetch related
    from django.db.models import Prefetch

    categories = Category.objects.prefetch_related(
        Prefetch(
            'articles',
            queryset=Article.objects.filter(published=True)
        )
    )

Q Objects
---------

Complex Conditions
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.db.models import Q

    # OR conditions
    articles = Article.objects.filter(
        Q(title__en__icontains='django') |
        Q(title__es__icontains='django')
    )

    # NOT conditions
    articles = Article.objects.filter(
        ~Q(title__en='Deprecated')
    )

    # Nested conditions
    articles = Article.objects.filter(
        Q(published=True) &
        (Q(title__en__icontains='python') |
         Q(title__es__icontains='python'))
    )

F Objects
---------

Field Comparisons
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.db.models import F

    # Compare localized fields
    # Note: Requires extracting values first
    from i18n_fields import LocalizedRef

    articles = Article.objects.annotate(
        title_en=LocalizedRef('title', 'en'),
        title_es=LocalizedRef('title', 'es')
    ).filter(
        title_en=F('title_es')  # Where English equals Spanish
    )

Raw SQL
-------

When Necessary
~~~~~~~~~~~~~~

For complex queries not supported by the ORM:

.. code-block:: python

    # Query specific JSON key
    articles = Article.objects.raw(
        "SELECT * FROM myapp_article WHERE title->>'en' = %s",
        ['Hello World']
    )

    # JSON array aggregation (PostgreSQL)
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                category_id,
                json_agg(title->'en') as titles
            FROM myapp_article
            GROUP BY category_id
        """)
        results = cursor.fetchall()

Performance Optimization
------------------------

Indexing
~~~~~~~~

Add indexes for frequently queried languages:

.. code-block:: python

    from django.contrib.postgres.indexes import GinIndex
    from django.db import models

    class Article(models.Model):
        title = LocalizedCharField(max_length=200)

        class Meta:
            # PostgreSQL GIN index for JSON field
            indexes = [
                GinIndex(fields=['title']),
            ]

Only Fetch Needed Data
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from i18n_fields import L

    # Only get id and English title
    articles = Article.objects.values('id', title=L('title', 'en'))

    # Use iterator for large querysets
    for article in Article.objects.iterator(chunk_size=100):
        process(article)

Bulk Operations
---------------

Bulk Create
~~~~~~~~~~~

.. code-block:: python

    articles = [
        Article(
            title={'en': f'Article {i}', 'es': f'Artículo {i}'},
            content={'en': f'Content {i}'}
        )
        for i in range(100)
    ]

    Article.objects.bulk_create(articles)

Bulk Update
~~~~~~~~~~~

.. code-block:: python

    # Update specific language for all articles
    Article.objects.filter(category='tech').update(
        title={'en': 'Tech Article', 'es': 'Artículo Técnico'}
    )

Complete Example
----------------

Here's a comprehensive query example:

.. code-block:: python

    from django.db.models import Q, Count, Prefetch
    from django.utils import translation
    from i18n_fields import L, LocalizedRef

    # Complex query with filtering, ordering, and prefetching
    with translation.override('en'):
        articles = Article.objects.filter(
            Q(published=True) &
            (Q(title__en__icontains='python') |
             Q(title__es__icontains='python'))
        ).select_related(
            'author',
            'category'
        ).prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.objects.filter(approved=True)
            )
        ).annotate(
            title_text=LocalizedRef('title'),
            comment_count=Count('comments')
        ).order_by(
            '-created_at',
            L('title')
        )

        for article in articles:
            print(f"Title: {article.title_text}")
            print(f"Comments: {article.comment_count}")
            print(f"Author: {article.author.name}")

Best Practices
--------------

1. **Use L() for Ordering**

   Always use ``L()`` for ordering by localized fields:

   .. code-block:: python

       # Good
       articles = Article.objects.order_by(L('title'))

       # Don't do this
       articles = Article.objects.order_by('title')  # Won't work as expected

2. **Filter by Specific Languages**

   Use language-specific lookups for precise filtering:

   .. code-block:: python

       # Good
       articles = Article.objects.filter(title__en__icontains='python')

       # Less precise
       articles = Article.objects.filter(title__icontains='python')

3. **Optimize with Select/Prefetch**

   Always use select_related and prefetch_related:

   .. code-block:: python

       articles = Article.objects.select_related(
           'author', 'category'
       ).prefetch_related('tags')

4. **Use values() When Possible**

   If you don't need model instances, use values():

   .. code-block:: python

       # Faster
       data = Article.objects.values('id', title=L('title', 'en'))

5. **Be Careful with Raw SQL**

   Prefer ORM when possible, but use raw SQL for complex queries:

   .. code-block:: python

       # Only when ORM can't do it
       results = Article.objects.raw("SELECT ...")

Next Steps
----------

- :doc:`../reference/fields` - Complete field reference
- :doc:`../reference/expressions` - Expression reference
- :doc:`basic-usage` - Basic usage patterns
