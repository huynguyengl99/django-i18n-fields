"""Pytest configuration for i18n_fields tests.

This module configures Django settings for tests using PostgreSQL database.
"""

import os
import shutil
from pathlib import Path

import django
from django.apps import apps
from django.conf import settings

from environs import Env

# Load environment variables from .env.test
env = Env()
ROOT_DIR = Path(__file__).parent.parent
env_file = ROOT_DIR / ".env.test"

if env_file.exists():
    env.read_env(str(env_file), recurse=False)
else:
    env.read_env()

# Configure Django settings for tests if not already configured
# (e.g., when running standalone without sandbox settings)
if not settings.configured:
    # Database options for Django 5.1+
    _db_options = {}
    if django.VERSION >= (5, 1):
        _db_options["pool"] = True

    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": env.str("POSTGRES_DB", "django_i18n_fields_test"),
                "USER": env.str("POSTGRES_USER", "postgres"),
                "PASSWORD": env.str("POSTGRES_PASSWORD", ""),
                "HOST": env.str("POSTGRES_HOST", "localhost"),
                "PORT": env.int("POSTGRES_PORT", 5432),
                "OPTIONS": _db_options,
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.admin",
            "django.contrib.sessions",
            "django.contrib.messages",
            "rest_framework",
            "i18n_fields",
        ],
        LANGUAGE_CODE="en",
        LANGUAGES=[
            ("en", "English"),
            ("nl", "Dutch"),
            ("fr", "French"),
            ("de", "German"),
            ("es", "Spanish"),
            ("it", "Italian"),
            ("pt", "Portuguese"),
            ("ja", "Japanese"),
        ],
        USE_I18N=True,
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        I18N_FIELDS={
            "DISPLAY": "tab",
            "FALLBACKS": {"nl": ["en"], "fr": ["en"], "de": ["en"]},
            "MAX_RETRIES": 100,
            "REGISTER_LOOKUPS": True,
        },
        MEDIA_ROOT="/tmp/i18n_fields_test_media",
        MEDIA_URL="/media/",
        # Required for admin
        ROOT_URLCONF="",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ],
        SECRET_KEY="test-secret-key",
    )

# Only call django.setup() if it hasn't been done yet
if not apps.ready:
    django.setup()


def pytest_sessionfinish(session, exitstatus):
    """Clean up media files after tests."""
    media_root = getattr(settings, "MEDIA_ROOT", None)
    if media_root and os.path.exists(media_root):
        if "i18n_fields_test" in media_root or "media-testing" in media_root:
            shutil.rmtree(media_root, ignore_errors=True)
