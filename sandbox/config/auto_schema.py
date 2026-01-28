"""Custom AutoSchema for DRF Spectacular with Accept-Language header support."""

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import OpenApiParameter


class CustomAutoSchema(AutoSchema):
    """
    Custom AutoSchema for DRF Spectacular.

    This class extends the default AutoSchema provided by DRF Spectacular to add
    global parameters to the OpenAPI schema. Specifically, it adds an "Accept-Language"
    header parameter to all endpoints.

    Attributes:
        global_params (list): A list of global OpenAPI parameters to be added to all endpoints.

    Configuration:
        To use this custom schema in Django REST Framework, update your settings:

        .. code-block:: python

            # Rest framework
            REST_FRAMEWORK = {
                "DEFAULT_RENDERER_CLASSES": [
                    "rest_framework.renderers.JSONRenderer",
                ],
                "DEFAULT_SCHEMA_CLASS": "config.auto_schema.CustomAutoSchema",
            }
    """

    global_params = [
        OpenApiParameter(
            name="Accept-Language",
            type=str,
            location=OpenApiParameter.HEADER,
            description="Language code for localized content (e.g., en, nl, fr, de, es, it, pt, ja). "
            "Determines which translation is returned for localized fields.",
            required=False,
        )
    ]

    def get_override_parameters(self):
        """
        Get the override parameters for the schema.

        This method extends the default parameters with the global parameters defined in
        the `global_params` attribute.

        Returns:
            list: A list of OpenAPI parameters.
        """
        params = super().get_override_parameters()
        return params + self.global_params
