"""DRF serializers for models with localized fields.

This module provides a ModelSerializer subclass that automatically maps
localized field types to appropriate DRF serializer fields.
"""

from typing import Any, Generic

from django.db.models import Model
from rest_framework.serializers import ModelSerializer

from typing_extensions import TypeVar

from ..fields import (
    LocalizedBooleanField,
    LocalizedCharField,
    LocalizedField,
    LocalizedFileField,
    LocalizedFloatField,
    LocalizedIntegerField,
    LocalizedTextField,
    LocalizedUniqueSlugField,
)
from . import serializer_fields

_MT = TypeVar("_MT", bound=Model, default=Model)


class LocalizedModelSerializer(ModelSerializer[_MT], Generic[_MT]):
    """A ModelSerializer that automatically maps localized fields to DRF fields.

    This serializer handles the serialization and deserialization of localized
    fields by mapping them to their appropriate DRF field counterparts. The
    localized fields will be serialized using the current active language.

    Field Mapping:
        - LocalizedField -> CharField
        - LocalizedCharField -> CharField
        - LocalizedTextField -> CharField
        - LocalizedUniqueSlugField -> SlugField
        - LocalizedFileField -> FileField
        - LocalizedIntegerField -> IntegerField
        - LocalizedFloatField -> FloatField
        - LocalizedBooleanField -> BooleanField

    Example:
        from i18n_fields.drf import LocalizedModelSerializer

        class ArticleSerializer(LocalizedModelSerializer):
            class Meta:
                model = Article
                fields = ['id', 'title', 'content', 'rating']

        # When serialized, the localized fields will return values in
        # the current active language:
        # {"id": 1, "title": "Hello", "content": "...", "rating": 4.5}
    """

    serializer_field_mapping = (  # pyright: ignore
        ModelSerializer.serializer_field_mapping.copy()  # pyright: ignore
    )

    # Map localized fields to custom serializer fields that handle LocalizedValue translation
    # Note: More specific types must be mapped first since they inherit from LocalizedField
    serializer_field_mapping[LocalizedUniqueSlugField] = (
        serializer_fields.LocalizedSlugField
    )
    serializer_field_mapping[LocalizedFileField] = serializer_fields.LocalizedFileField
    serializer_field_mapping[LocalizedIntegerField] = (
        serializer_fields.LocalizedIntegerField
    )
    serializer_field_mapping[LocalizedFloatField] = (
        serializer_fields.LocalizedFloatField
    )
    serializer_field_mapping[LocalizedBooleanField] = (
        serializer_fields.LocalizedBooleanField
    )
    serializer_field_mapping[LocalizedTextField] = serializer_fields.LocalizedCharField
    serializer_field_mapping[LocalizedCharField] = serializer_fields.LocalizedCharField
    serializer_field_mapping[LocalizedField] = serializer_fields.LocalizedCharField

    def build_standard_field(
        self,
        field_name: str,
        model_field: Any,
    ) -> tuple[type, dict[str, Any]]:
        """Build a standard field for the given model field.

        Overridden to handle localized fields appropriately, ensuring that
        allow_blank is set for string-based localized fields when blank=True.
        Also removes JSONField-specific kwargs that don't apply to the mapped
        serializer field types.

        Args:
            field_name: The name of the field.
            model_field: The model field instance.

        Returns:
            Tuple of (field_class, field_kwargs).
        """
        (
            field_class,  # pyright: ignore[reportUnknownVariableType]
            field_kwargs,
        ) = super().build_standard_field(  # pyright: ignore[reportUnknownMemberType]
            field_name, model_field
        )

        # Check if this is a localized field
        is_localized_field = isinstance(
            model_field,
            LocalizedField
            | LocalizedCharField
            | LocalizedTextField
            | LocalizedIntegerField
            | LocalizedFloatField
            | LocalizedBooleanField
            | LocalizedFileField
            | LocalizedUniqueSlugField,
        )

        if is_localized_field:
            # Remove JSONField-specific kwargs that don't apply to
            # the mapped serializer field types
            field_kwargs.pop("encoder", None)
            field_kwargs.pop("decoder", None)

            # Check for non-string field types first (they inherit from LocalizedField)
            is_non_string_field = isinstance(
                model_field,
                LocalizedIntegerField
                | LocalizedFloatField
                | LocalizedBooleanField
                | LocalizedFileField
                | LocalizedUniqueSlugField,
            )

            if is_non_string_field:
                # Non-string fields don't accept allow_blank
                field_kwargs.pop("allow_blank", None)

                # Handle optional fields
                if model_field.blank or model_field.null:
                    field_kwargs["required"] = False
                    field_kwargs["allow_null"] = True
            # String-based localized fields (LocalizedField, LocalizedCharField, LocalizedTextField)
            elif model_field.blank:
                field_kwargs["allow_blank"] = True
                field_kwargs["required"] = False

        return field_class, field_kwargs  # pyright: ignore[reportUnknownVariableType]
