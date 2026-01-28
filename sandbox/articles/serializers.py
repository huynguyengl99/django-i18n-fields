"""Serializers for the articles app."""

from rest_framework import serializers

from i18n_fields.drf import LocalizedModelSerializer

from .models import Article, Category, Tag


class CategorySerializer(LocalizedModelSerializer):
    """Serializer for Category model with localized fields."""

    class Meta:
        model = Category
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


class TagSerializer(LocalizedModelSerializer):
    """Serializer for Tag model with localized fields."""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class ArticleSerializer(LocalizedModelSerializer):
    """Serializer for Article model with localized fields."""

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source="tags",
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "content",
            "view_count",
            "rating",
            "is_featured",
            "category",
            "category_id",
            "tags",
            "tag_ids",
            "created_at",
            "updated_at",
            "published",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class ArticleListSerializer(LocalizedModelSerializer):
    """Lightweight serializer for listing articles."""

    category = CategorySerializer(read_only=True)
    tags_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "is_featured",
            "category",
            "tags_count",
            "created_at",
            "published",
        ]
        read_only_fields = fields

    def get_tags_count(self, obj: Article) -> int:
        """Get the number of tags associated with the article."""
        return obj.tags.count()
