"""Fake model utilities for creating test models dynamically."""

import uuid
from typing import Any

from django.db import connection, models

from i18n_fields.mixins import AtomicSlugRetryMixin


def define_fake_model(
    fields: dict[str, models.Field] | None = None,
    model_base: type = models.Model,
    meta_options: dict[str, Any] | None = None,
    use_slug_retry: bool = False,
) -> type[models.Model]:
    """Define a fake model class without creating the database table.

    Args:
        fields: Dictionary of field name to field instance.
        model_base: Base class for the model.
        meta_options: Options to pass to the Meta class.
        use_slug_retry: Whether to add AtomicSlugRetryMixin.

    Returns:
        A new model class.
    """
    name = str(uuid.uuid4()).replace("-", "")[:8]

    meta_options = meta_options or {}
    if "app_label" not in meta_options:
        meta_options["app_label"] = "tests"

    attributes: dict[str, Any] = {
        "__module__": __name__,
        "__name__": name,
        "Meta": type("Meta", (), meta_options),
    }

    if fields:
        attributes.update(fields)

    if use_slug_retry:
        return type(name, (AtomicSlugRetryMixin, model_base), attributes)

    return type(name, (model_base,), attributes)


def get_fake_model(
    fields: dict[str, models.Field] | None = None,
    model_base: type = models.Model,
    meta_options: dict[str, Any] | None = None,
    use_slug_retry: bool = False,
) -> type[models.Model]:
    """Create a fake model and its database table for testing.

    This creates an actual database table that will be cleaned up
    when the connection is closed.

    Args:
        fields: Dictionary of field name to field instance.
        model_base: Base class for the model.
        meta_options: Options to pass to the Meta class.
        use_slug_retry: Whether to add AtomicSlugRetryMixin.

    Returns:
        A new model class with database table created.
    """
    model = define_fake_model(fields, model_base, meta_options, use_slug_retry)

    # Disable constraint checks for SQLite compatibility
    with connection.constraint_checks_disabled():
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model)

    return model


def cleanup_fake_model(model: type[models.Model]) -> None:
    """Clean up a fake model's database table.

    Args:
        model: The model class to clean up.
    """
    # Disable constraint checks for SQLite compatibility
    with connection.constraint_checks_disabled():
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(model)
