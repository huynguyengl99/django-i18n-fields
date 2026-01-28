Expressions Reference
=====================

This page documents query expressions for localized fields.

LocalizedRef
------------

.. class:: LocalizedRef(name, lang=None)

   Query expression that selects a value in a specific language from a localized field.

   **Parameters:**

   - ``name`` (str): The field/column name
   - ``lang`` (str | None): Language code (uses active language if None)

   **Inherits From:** ``KeyTextTransform`` (Django's JSON field transform)

   **Usage:**

   Can be used in:

   - ``annotate()`` - Add computed fields
   - ``values()`` - Select specific values
   - ``order_by()`` - Sort by localized content
   - ``filter()`` - Filter by localized values (less common)
   - ``update()`` - Update with computed values

   **Example:**

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

       # Use in values()
       data = Article.objects.values(
           'id',
           title=LocalizedRef('title', 'en')
       )

       # Order by localized field
       articles = Article.objects.order_by(LocalizedRef('title'))

   **With Aggregations:**

   .. code-block:: python

       from django.db.models import Count

       # Count articles by first letter of English title
       from django.db.models.functions import Left

       stats = Article.objects.annotate(
           title_en=LocalizedRef('title', 'en'),
           first_letter=Left('title_en', 1)
       ).values('first_letter').annotate(
           count=Count('id')
       )

   **With Other Functions:**

   .. code-block:: python

       from django.db.models.functions import Upper, Length

       # Convert to uppercase
       articles = Article.objects.annotate(
           title_upper=Upper(LocalizedRef('title', 'en'))
       )

       # Get length
       articles = Article.objects.annotate(
           title_length=Length(LocalizedRef('title', 'en'))
       )

L()
---

.. function:: L(name, lang=None)

   Shorthand function for ``LocalizedRef``.

   **Parameters:**

   - ``name`` (str): The field/column name
   - ``lang`` (str | None): Language code (uses active language if None)

   **Returns:** ``LocalizedRef`` instance

   **Example:**

   .. code-block:: python

       from i18n_fields import L

       # Instead of LocalizedRef('title', 'en')
       articles = Article.objects.order_by(L('title', 'en'))

       # Current language
       articles = Article.objects.order_by(L('title'))

       # In values()
       data = Article.objects.values('id', title=L('title'))

   **Why Use L()?**

   - Shorter and more readable
   - Commonly used in queries
   - Follows Django's convention (like F() and Q())

Common Use Cases
----------------

Ordering
~~~~~~~~

Order by localized fields in different languages:

.. code-block:: python

    from i18n_fields import L

    # Order by current language
    Article.objects.order_by(L('title'))

    # Order by English title
    Article.objects.order_by(L('title', 'en'))

    # Descending order
    Article.objects.order_by(L('title').desc())

    # Multiple fields
    Article.objects.order_by(L('category'), L('title'))

Annotations
~~~~~~~~~~~

Add computed fields based on localized content:

.. code-block:: python

    from i18n_fields import LocalizedRef
    from django.db.models.functions import Upper, Concat
    from django.db.models import Value, CharField

    # Add uppercase title
    articles = Article.objects.annotate(
        title_upper=Upper(LocalizedRef('title', 'en'))
    )

    # Concatenate with string
    articles = Article.objects.annotate(
        full_title=Concat(
            LocalizedRef('title', 'en'),
            Value(' - Article'),
            output_field=CharField()
        )
    )

    # Multiple languages
    articles = Article.objects.annotate(
        title_en=LocalizedRef('title', 'en'),
        title_es=LocalizedRef('title', 'es'),
        title_fr=LocalizedRef('title', 'fr')
    )

Values Queries
~~~~~~~~~~~~~~

Extract specific language values:

.. code-block:: python

    from i18n_fields import L

    # Get English titles
    titles = Article.objects.values_list(L('title', 'en'), flat=True)

    # Get multiple fields
    data = Article.objects.values(
        'id',
        'created_at',
        title=L('title', 'en'),
        content=L('content', 'en')
    )

    # Multiple languages
    data = Article.objects.values(
        'id',
        title_en=L('title', 'en'),
        title_es=L('title', 'es')
    )

Filtering
~~~~~~~~~

Filter by localized values (note: direct field lookups are usually better):

.. code-block:: python

    from i18n_fields import LocalizedRef
    from django.db.models import Q

    # Filter by annotation
    articles = Article.objects.annotate(
        title_en=LocalizedRef('title', 'en')
    ).filter(title_en='Hello World')

    # Better: use direct lookup
    articles = Article.objects.filter(title__en='Hello World')

Aggregations
~~~~~~~~~~~~

Aggregate localized data:

.. code-block:: python

    from django.db.models import Count, Avg
    from i18n_fields import LocalizedRef

    # Count by category with English titles
    stats = Article.objects.annotate(
        title_en=LocalizedRef('title', 'en')
    ).values('category').annotate(
        count=Count('id')
    )

    # Average rating by language
    from django.db.models import Case, When, IntegerField

    avg_rating = Article.objects.annotate(
        rating_en=LocalizedRef('rating', 'en')
    ).aggregate(
        avg=Avg('rating_en')
    )

Advanced Examples
-----------------

Conditional Expressions
~~~~~~~~~~~~~~~~~~~~~~~

Use with Case/When:

.. code-block:: python

    from django.db.models import Case, When, Value, CharField
    from i18n_fields import LocalizedRef

    # Choose title based on availability
    articles = Article.objects.annotate(
        display_title=Case(
            When(
                title__en__isnull=False,
                then=LocalizedRef('title', 'en')
            ),
            When(
                title__es__isnull=False,
                then=LocalizedRef('title', 'es')
            ),
            default=Value('No title'),
            output_field=CharField()
        )
    )

Subqueries
~~~~~~~~~~

Use in subqueries:

.. code-block:: python

    from django.db.models import OuterRef, Subquery
    from i18n_fields import LocalizedRef

    # Get latest article title for each author
    latest_articles = Article.objects.filter(
        author=OuterRef('pk')
    ).order_by('-created_at')

    authors = Author.objects.annotate(
        latest_article_title=Subquery(
            latest_articles.values(
                title=LocalizedRef('title', 'en')
            )[:1]
        )
    )

Window Functions
~~~~~~~~~~~~~~~~

Use with window functions (PostgreSQL):

.. code-block:: python

    from django.db.models import F, Window
    from django.db.models.functions import RowNumber
    from i18n_fields import LocalizedRef

    # Rank articles by title
    articles = Article.objects.annotate(
        title_en=LocalizedRef('title', 'en'),
        rank=Window(
            expression=RowNumber(),
            order_by=F('title_en').asc()
        )
    )

Related Fields
~~~~~~~~~~~~~~

Access localized fields through relations:

.. code-block:: python

    from i18n_fields import L

    # Order by related localized field
    comments = Comment.objects.order_by(
        L('article__title', 'en')
    )

    # Annotate with related localized field
    comments = Comment.objects.annotate(
        article_title=LocalizedRef('article__title', 'en')
    )

Performance Considerations
--------------------------

Database Indexes
~~~~~~~~~~~~~~~~

Consider adding indexes for frequently queried languages:

.. code-block:: python

    from django.contrib.postgres.indexes import GinIndex

    class Article(models.Model):
        title = LocalizedCharField(max_length=200)

        class Meta:
            indexes = [
                # PostgreSQL GIN index
                GinIndex(fields=['title']),
            ]

Query Optimization
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from i18n_fields import L

    # Good: Single annotation
    articles = Article.objects.annotate(
        title_en=L('title', 'en')
    ).order_by('title_en')

    # Less efficient: Multiple queries
    articles = Article.objects.all()
    sorted_articles = sorted(articles, key=lambda a: a.title.get('en'))

Batch Operations
~~~~~~~~~~~~~~~~

Use annotations for batch processing:

.. code-block:: python

    # Process in batches
    articles = Article.objects.annotate(
        title_en=L('title', 'en')
    ).values('id', 'title_en')

    for batch in batch_qs(articles, batch_size=1000):
        process_batch(batch)

Limitations
-----------

1. **Database-Specific**

   Some features require specific databases:

   - GIN indexes: PostgreSQL only
   - Window functions: PostgreSQL, MySQL 8.0+

2. **JSON Path Limitations**

   Complex JSON path queries may not work:

   .. code-block:: python

       # May not work
       articles = Article.objects.filter(
           title__en__in=['Hello', 'World']
       )

3. **Type Conversions**

   Database returns string values for JSON fields. Type conversion happens in Python:

   .. code-block:: python

       # Integer comparison may not work as expected
       products = Product.objects.annotate(
           stock_en=L('stock', 'en')
       ).filter(stock_en__gt=10)  # May compare as strings

Best Practices
--------------

1. **Use L() for Readability**

   Prefer ``L()`` over ``LocalizedRef`` for brevity:

   .. code-block:: python

       # Good
       articles = Article.objects.order_by(L('title'))

       # More verbose
       from i18n_fields import LocalizedRef
       articles = Article.objects.order_by(LocalizedRef('title'))

2. **Specify Language When Needed**

   Be explicit about language for consistent results:

   .. code-block:: python

       # Good - explicit
       articles = Article.objects.order_by(L('title', 'en'))

       # May vary based on active language
       articles = Article.objects.order_by(L('title'))

3. **Use Direct Lookups for Filtering**

   Prefer field lookups over expressions for filtering:

   .. code-block:: python

       # Good
       articles = Article.objects.filter(title__en='Hello')

       # Less efficient
       articles = Article.objects.annotate(
           title_en=L('title', 'en')
       ).filter(title_en='Hello')

4. **Combine with select_related**

   Optimize queries with related fields:

   .. code-block:: python

       articles = Article.objects.select_related(
           'author', 'category'
       ).annotate(
           title_en=L('title', 'en')
       ).order_by('title_en')

See Also
--------

- :doc:`../user-guides/advanced-queries` - Advanced querying guide
- :doc:`fields` - Localized field types
- `Django Expressions <https://docs.djangoproject.com/en/stable/ref/models/expressions/>`_
