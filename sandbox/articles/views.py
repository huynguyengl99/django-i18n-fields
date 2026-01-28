"""Views for the articles app."""

from django.utils import translation
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Article, Category, Tag
from .serializers import (
    ArticleListSerializer,
    ArticleSerializer,
    CategorySerializer,
    TagSerializer,
)


class LanguageHeaderMixin:
    """Mixin to handle Accept-Language header for all viewsets."""

    def initialize_request(self, request, *args, **kwargs):
        """Initialize request and set language from Accept-Language header."""
        request = super().initialize_request(request, *args, **kwargs)  # type: ignore[misc]

        # Get Accept-Language header
        accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE")
        if accept_language:
            # Extract the first language code (e.g., "en-US" -> "en")
            language_code = accept_language.split(",")[0].split("-")[0].strip()
            # Activate the language for this request
            translation.activate(language_code)
            request.LANGUAGE_CODE = language_code  # type: ignore[attr-defined]

        return request


@extend_schema_view(
    list=extend_schema(
        summary="List all categories",
        description="Returns a list of all categories with localized names and descriptions.",
    ),
    retrieve=extend_schema(
        summary="Get a category",
        description="Returns a single category with localized content.",
    ),
    create=extend_schema(
        summary="Create a category",
        description="Creates a new category with localized fields.",
    ),
    update=extend_schema(
        summary="Update a category",
        description="Updates an existing category's localized fields.",
    ),
    partial_update=extend_schema(
        summary="Partially update a category",
        description="Partially updates an existing category's localized fields.",
    ),
    destroy=extend_schema(
        summary="Delete a category",
        description="Deletes a category.",
    ),
)
class CategoryViewSet(LanguageHeaderMixin, viewsets.ModelViewSet):
    """ViewSet for managing categories with localized content."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all tags",
        description="Returns a list of all tags with localized names.",
    ),
    retrieve=extend_schema(
        summary="Get a tag",
        description="Returns a single tag with localized content.",
    ),
    create=extend_schema(
        summary="Create a tag",
        description="Creates a new tag with localized fields.",
    ),
    update=extend_schema(
        summary="Update a tag",
        description="Updates an existing tag's localized fields.",
    ),
    partial_update=extend_schema(
        summary="Partially update a tag",
        description="Partially updates an existing tag's localized fields.",
    ),
    destroy=extend_schema(
        summary="Delete a tag",
        description="Deletes a tag.",
    ),
)
class TagViewSet(LanguageHeaderMixin, viewsets.ModelViewSet):
    """ViewSet for managing tags with localized content."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all articles",
        description="Returns a paginated list of articles with localized content. "
        "The content language depends on the Accept-Language header.",
    ),
    retrieve=extend_schema(
        summary="Get an article",
        description="Returns a single article with full localized content.",
    ),
    create=extend_schema(
        summary="Create an article",
        description="Creates a new article with localized fields.",
    ),
    update=extend_schema(
        summary="Update an article",
        description="Updates an existing article's localized fields.",
    ),
    partial_update=extend_schema(
        summary="Partially update an article",
        description="Partially updates an existing article's localized fields.",
    ),
    destroy=extend_schema(
        summary="Delete an article",
        description="Deletes an article.",
    ),
)
class ArticleViewSet(LanguageHeaderMixin, viewsets.ModelViewSet):
    """ViewSet for managing articles with localized content."""

    queryset = Article.objects.select_related("category").prefetch_related("tags").all()

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == "list":
            return ArticleListSerializer
        return ArticleSerializer

    @extend_schema(
        summary="Publish an article",
        description="Marks an article as published.",
        request=None,
        responses={200: ArticleSerializer},
    )
    @action(detail=True, methods=["post"])
    def publish(self, request: Request, pk=None) -> Response:
        """Publish an article."""
        article = self.get_object()
        article.published = True
        article.save()
        serializer = self.get_serializer(article)
        return Response(serializer.data)

    @extend_schema(
        summary="Unpublish an article",
        description="Marks an article as unpublished (draft).",
        request=None,
        responses={200: ArticleSerializer},
    )
    @action(detail=True, methods=["post"])
    def unpublish(self, request: Request, pk=None) -> Response:
        """Unpublish an article."""
        article = self.get_object()
        article.published = False
        article.save()
        serializer = self.get_serializer(article)
        return Response(serializer.data)

    @extend_schema(
        summary="Get featured articles",
        description="Returns a list of featured articles with localized content.",
        responses={200: ArticleListSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def featured(self, request: Request) -> Response:
        """Get all featured articles."""
        # Use active_ref to get the value in the current language
        from django.utils import translation
        lang = translation.get_language() or "en"

        # Filter using JSON field lookup for the current language
        queryset = self.get_queryset().filter(
            **{f"is_featured__{lang}": True},
            published=True
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ArticleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ArticleListSerializer(queryset, many=True)
        return Response(serializer.data)
