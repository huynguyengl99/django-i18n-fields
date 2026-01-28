"""Tests for the articles API with Accept-Language header support."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

import pytest

from articles.models import Article, Category, Tag


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def sample_category():
    """Create a sample category with multilingual content."""
    return Category.objects.create(
        name={
            "en": "Technology",
            "nl": "Technologie",
            "fr": "Technologie",
            "de": "Technologie",
            "es": "Tecnología",
        },
        description={
            "en": "Tech articles",
            "nl": "Tech artikelen",
            "fr": "Articles techniques",
            "de": "Tech-Artikel",
            "es": "Artículos técnicos",
        },
    )


@pytest.fixture
def sample_tag():
    """Create a sample tag with multilingual content."""
    return Tag.objects.create(
        name={
            "en": "Python",
            "nl": "Python",
            "fr": "Python",
            "de": "Python",
            "es": "Python",
        }
    )


@pytest.fixture
def sample_article(sample_category, sample_tag):
    """Create a sample article with multilingual content."""
    article = Article.objects.create(
        title={
            "en": "Introduction to Django",
            "nl": "Introductie tot Django",
            "fr": "Introduction à Django",
            "de": "Einführung in Django",
            "es": "Introducción a Django",
        },
        summary={
            "en": "Learn Django basics",
            "nl": "Leer Django basisprincipes",
            "fr": "Apprendre les bases de Django",
            "de": "Django Grundlagen lernen",
            "es": "Aprende los conceptos básicos de Django",
        },
        content={
            "en": "Django is a web framework",
            "nl": "Django is een webframework",
            "fr": "Django est un framework web",
            "de": "Django ist ein Web-Framework",
            "es": "Django es un framework web",
        },
        category=sample_category,
        published=True,
    )
    article.tags.add(sample_tag)
    return article


@pytest.mark.django_db
class TestAcceptLanguageHeader:
    """Test Accept-Language header functionality."""

    def test_article_list_english(self, api_client, sample_article):
        """Test fetching articles in English."""
        url = reverse("article-list")
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="en")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        article_data = response.data["results"][0]
        assert article_data["title"] == "Introduction to Django"
        assert article_data["summary"] == "Learn Django basics"

    def test_article_list_dutch(self, api_client, sample_article):
        """Test fetching articles in Dutch."""
        url = reverse("article-list")
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="nl")

        assert response.status_code == status.HTTP_200_OK
        article_data = response.data["results"][0]
        assert article_data["title"] == "Introductie tot Django"
        assert article_data["summary"] == "Leer Django basisprincipes"

    def test_article_list_french(self, api_client, sample_article):
        """Test fetching articles in French."""
        url = reverse("article-list")
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="fr")

        assert response.status_code == status.HTTP_200_OK
        article_data = response.data["results"][0]
        assert article_data["title"] == "Introduction à Django"
        assert article_data["summary"] == "Apprendre les bases de Django"

    def test_article_list_german(self, api_client, sample_article):
        """Test fetching articles in German."""
        url = reverse("article-list")
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="de")

        assert response.status_code == status.HTTP_200_OK
        article_data = response.data["results"][0]
        assert article_data["title"] == "Einführung in Django"
        assert article_data["summary"] == "Django Grundlagen lernen"

    def test_article_list_spanish(self, api_client, sample_article):
        """Test fetching articles in Spanish."""
        url = reverse("article-list")
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="es")

        assert response.status_code == status.HTTP_200_OK
        article_data = response.data["results"][0]
        assert article_data["title"] == "Introducción a Django"
        assert article_data["summary"] == "Aprende los conceptos básicos de Django"

    def test_article_detail_english(self, api_client, sample_article):
        """Test fetching article detail in English."""
        url = reverse("article-detail", kwargs={"pk": sample_article.pk})
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="en")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Introduction to Django"
        assert response.data["content"] == "Django is a web framework"

    def test_article_detail_dutch(self, api_client, sample_article):
        """Test fetching article detail in Dutch."""
        url = reverse("article-detail", kwargs={"pk": sample_article.pk})
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="nl")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Introductie tot Django"
        assert response.data["content"] == "Django is een webframework"

    def test_category_with_different_languages(self, api_client, sample_category):
        """Test fetching category in different languages."""
        url = reverse("category-detail", kwargs={"pk": sample_category.pk})

        # Test English
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="en")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Technology"
        assert response.data["description"] == "Tech articles"

        # Test Dutch
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="nl")
        assert response.data["name"] == "Technologie"
        assert response.data["description"] == "Tech artikelen"

        # Test French
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="fr")
        assert response.data["name"] == "Technologie"
        assert response.data["description"] == "Articles techniques"

    def test_language_fallback(self, api_client, sample_article):
        """Test that different languages return appropriate content."""
        url = reverse("article-detail", kwargs={"pk": sample_article.pk})

        # Request in English (available)
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="en")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Introduction to Django"

        # Request in Dutch (available)
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="nl")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Introductie tot Django"

        # Request in French (available)
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="fr")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Introduction à Django"


@pytest.mark.django_db
class TestArticleAPI:
    """Test article CRUD operations with multilingual content."""

    def test_create_article_with_multilingual_content(
        self, api_client, sample_category, sample_tag
    ):
        """Test creating an article with multilingual content."""
        url = reverse("article-list")
        data = {
            "title": {
                "en": "New Article",
                "nl": "Nieuw Artikel",
                "fr": "Nouvel Article",
            },
            "summary": {
                "en": "A new article",
                "nl": "Een nieuw artikel",
                "fr": "Un nouvel article",
            },
            "content": {
                "en": "Article content",
                "nl": "Artikel inhoud",
                "fr": "Contenu de l'article",
            },
            "category_id": sample_category.pk,
            "tag_ids": [sample_tag.pk],
            "published": True,
        }

        response = api_client.post(
            url, data, format="json", HTTP_ACCEPT_LANGUAGE="en"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Article"
        assert Article.objects.count() == 1

    def test_update_article_multilingual_content(self, api_client, sample_article):
        """Test updating article with multilingual content."""
        url = reverse("article-detail", kwargs={"pk": sample_article.pk})

        # Update title using PATCH
        data = {
            "title": {
                "en": "Updated Title",
                "nl": "Bijgewerkte Titel",
                "fr": "Titre Mis à Jour",
            }
        }

        response = api_client.patch(
            url, data, format="json", HTTP_ACCEPT_LANGUAGE="en"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"

        # Verify in Dutch
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="nl")
        assert response.data["title"] == "Bijgewerkte Titel"

    def test_partial_update_article(self, api_client, sample_article):
        """Test partial update of article."""
        url = reverse("article-detail", kwargs={"pk": sample_article.pk})
        data = {
            "published": False  # Simple field update, not localized
        }

        response = api_client.patch(
            url, data, format="json", HTTP_ACCEPT_LANGUAGE="en"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["published"] is False

        # Verify the article is still the same otherwise
        assert response.data["title"] == "Introduction to Django"

    def test_delete_article(self, api_client, sample_article):
        """Test deleting an article."""
        url = reverse("article-detail", kwargs={"pk": sample_article.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Article.objects.count() == 0


@pytest.mark.django_db
class TestArticleActions:
    """Test custom article actions."""

    def test_publish_article(self, api_client, sample_category):
        """Test publishing an article."""
        article = Article.objects.create(
            title={"en": "Draft Article"},
            content={"en": "Draft content"},
            category=sample_category,
            published=False,
        )

        url = reverse("article-publish", kwargs={"pk": article.pk})
        response = api_client.post(url, HTTP_ACCEPT_LANGUAGE="en")

        assert response.status_code == status.HTTP_200_OK
        article.refresh_from_db()
        assert article.published is True

    def test_unpublish_article(self, api_client, sample_article):
        """Test unpublishing an article."""
        url = reverse("article-unpublish", kwargs={"pk": sample_article.pk})
        response = api_client.post(url, HTTP_ACCEPT_LANGUAGE="en")

        assert response.status_code == status.HTTP_200_OK
        sample_article.refresh_from_db()
        assert sample_article.published is False

    def test_featured_articles(self, api_client, sample_category):
        """Test fetching featured articles."""
        # Create featured and non-featured articles
        Article.objects.create(
            title={"en": "Featured Article", "nl": "Uitgelicht Artikel"},
            content={"en": "Featured content", "nl": "Uitgelichte inhoud"},
            is_featured={"en": True, "nl": True},
            category=sample_category,
            published=True,
        )

        Article.objects.create(
            title={"en": "Normal Article"},
            content={"en": "Normal content"},
            is_featured={"en": False},
            category=sample_category,
            published=True,
        )

        url = reverse("article-featured")

        # Test in English
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="en")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == "Featured Article"

        # Test in Dutch
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="nl")
        assert response.data["results"][0]["title"] == "Uitgelicht Artikel"


@pytest.mark.django_db
class TestCategoryAPI:
    """Test category API endpoints."""

    def test_create_category(self, api_client):
        """Test creating a category."""
        url = reverse("category-list")
        data = {
            "name": {
                "en": "Science",
                "nl": "Wetenschap",
                "fr": "Science",
            },
            "description": {
                "en": "Science articles",
                "nl": "Wetenschaps artikelen",
                "fr": "Articles scientifiques",
            },
        }

        response = api_client.post(
            url, data, format="json", HTTP_ACCEPT_LANGUAGE="en"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Science"
        assert Category.objects.count() == 1

    def test_list_categories(self, api_client, sample_category):
        """Test listing categories."""
        url = reverse("category-list")
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="en")

        assert response.status_code == status.HTTP_200_OK
        # Categories use pagination
        if "results" in response.data:
            assert len(response.data["results"]) == 1
            assert response.data["results"][0]["name"] == "Technology"
        else:
            assert len(response.data) == 1
            assert response.data[0]["name"] == "Technology"


@pytest.mark.django_db
class TestTagAPI:
    """Test tag API endpoints."""

    def test_create_tag(self, api_client):
        """Test creating a tag."""
        url = reverse("tag-list")
        data = {
            "name": {
                "en": "Django",
                "nl": "Django",
                "fr": "Django",
            }
        }

        response = api_client.post(
            url, data, format="json", HTTP_ACCEPT_LANGUAGE="en"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Django"

    def test_list_tags(self, api_client, sample_tag):
        """Test listing tags."""
        url = reverse("tag-list")
        response = api_client.get(url, HTTP_ACCEPT_LANGUAGE="nl")

        assert response.status_code == status.HTTP_200_OK
        # Tags use pagination
        if "results" in response.data:
            assert len(response.data["results"]) == 1
            assert response.data["results"][0]["name"] == "Python"
        else:
            assert len(response.data) == 1
            assert response.data[0]["name"] == "Python"
