from typing import Any

from django.forms import Textarea
from django.forms.renderers import BaseRenderer
from django.template.loader import get_template
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from martor.settings import (  # pyright: ignore[reportMissingTypeStubs]
    MARTOR_ALTERNATIVE_CSS_FILE_THEME,
    MARTOR_ALTERNATIVE_JQUERY_JS_FILE,
    MARTOR_ALTERNATIVE_JS_FILE_THEME,
    MARTOR_CSRF_COOKIE_NAME,
    MARTOR_ENABLE_ADMIN_CSS,
    MARTOR_ENABLE_CONFIGS,
    MARTOR_MARKDOWN_BASE_EMOJI_URL,
    MARTOR_MARKDOWNIFY_TIMEOUT,
    MARTOR_SEARCH_USERS_URL,
    MARTOR_TOOLBAR_BUTTONS,
    MARTOR_UPLOAD_URL,
)
from martor.widgets import (  # pyright: ignore[reportMissingTypeStubs]
    AdminMartorWidget,
    MartorWidget,
    get_theme,
)

from i18n_fields.widgets import AdminLocalizedFieldWidget, LocalizedFieldWidget


class LocalizedMartorWidget(LocalizedFieldWidget):
    widget = MartorWidget


class AdminLocalizedMartorWidget(AdminLocalizedFieldWidget):
    widget = AdminMartorWidget

    def markdown_render(
        self,
        name: str,
        value: str,
        attrs: dict[str, Any] | None = None,
        renderer: BaseRenderer | None = None,
        **kwargs: Any,
    ) -> SafeString:
        random_string = get_random_string(10)
        assert attrs is not None
        attrs["id"] = attrs["id"] + "-" + random_string

        # Make the settings the default attributes to pass
        attributes_to_pass: dict[str, Any] = {
            "data-enable-configs": MARTOR_ENABLE_CONFIGS,
            "data-markdownfy-url": reverse("martor_markdownfy"),
            "data-csrf-cookie-name": MARTOR_CSRF_COOKIE_NAME,
        }

        if MARTOR_UPLOAD_URL:
            attributes_to_pass["data-upload-url"] = MARTOR_UPLOAD_URL
        if MARTOR_SEARCH_USERS_URL:
            attributes_to_pass["data-search-users-url"] = MARTOR_SEARCH_USERS_URL
        if MARTOR_MARKDOWN_BASE_EMOJI_URL:
            attributes_to_pass["data-base-emoji-url"] = MARTOR_MARKDOWN_BASE_EMOJI_URL
        if MARTOR_MARKDOWNIFY_TIMEOUT:
            attributes_to_pass["data-save-timeout"] = MARTOR_MARKDOWNIFY_TIMEOUT

        # Make sure that the martor value is in the class attr passed in
        if "class" in attrs:
            attrs["class"] += " martor"
        else:
            attrs["class"] = "martor"

        # Update and overwrite with the attributes passed in
        attributes_to_pass.update(attrs)

        # Update and overwrite with any attributes that are on the widget
        # itself. This is also the only way we can push something in without
        # being part of the render chain.
        attributes_to_pass.update(self.attrs)

        template = get_template(f"martor/{get_theme()}/editor.html")
        emoji_enabled = MARTOR_ENABLE_CONFIGS.get("emoji") == "true"
        mentions_enabled = MARTOR_ENABLE_CONFIGS.get("mention") == "true"

        field_name: str = name + "-" + random_string

        textarea = Textarea(attrs=attributes_to_pass)
        rendered_textarea = textarea.render(name, value)

        res = template.render(
            {
                "martor": rendered_textarea,
                "field_name": field_name,
                "emoji_enabled": emoji_enabled,
                "mentions_enabled": mentions_enabled,
                "toolbar_buttons": MARTOR_TOOLBAR_BUTTONS,
            }
        )

        return format_html(
            '<div class="main-martor" data-field-name="{}">{}</div>',
            field_name,
            mark_safe(res),
        )

    def render(
        self,
        name: str,
        value: Any,
        attrs: dict[str, Any] | None = None,
        renderer: BaseRenderer | None = None,
    ) -> SafeString:
        context = self.get_context(name, value, attrs)
        widget = context["widget"]
        md = self.markdown_render(widget["name"], "", attrs)
        context["widget"]["md"] = md
        return self._render(self.template_name, context, renderer)  # type: ignore[attr-defined,no-any-return]

    class Media:
        selected_theme = get_theme()
        css: dict[str, tuple[str, ...]] = {
            "all": (
                "plugins/css/ace.min.css",
                "plugins/css/highlight.min.css",
                f"martor/css/martor.{selected_theme}.min.css",
            )
        }

        if MARTOR_ENABLE_ADMIN_CSS:
            admin_theme = ("martor/css/martor-admin.min.css",)
            css["all"] = admin_theme + css["all"]

        js: tuple[str, ...] = (
            "plugins/js/ace.js",
            "plugins/js/mode-markdown.js",
            "plugins/js/ext-language_tools.js",
            "plugins/js/theme-github.js",
            "plugins/js/highlight.min.js",
            "plugins/js/emojis.min.js",
            f"martor/js/martor.{selected_theme}.js",
        )

        # Adding the following scripts to the end
        # of the tuple in case it affects behaviour.
        # spellcheck configuration
        if MARTOR_ENABLE_CONFIGS.get("spellcheck") == "true":
            js = ("plugins/js/typo.js", "plugins/js/spellcheck.js") + js

        # support alternative vendor theme file like: bootstrap, semantic)
        # 1. vendor css theme
        if MARTOR_ALTERNATIVE_CSS_FILE_THEME:
            css["all"] = (MARTOR_ALTERNATIVE_CSS_FILE_THEME,) + css["all"]
        else:
            css["all"] = (f"plugins/css/{selected_theme}.min.css",) + css["all"]

        # 2. vendor js theme
        if MARTOR_ALTERNATIVE_JS_FILE_THEME:
            js = (MARTOR_ALTERNATIVE_JS_FILE_THEME,) + js
        else:
            js = (f"plugins/js/{selected_theme}.min.js",) + js

        # 3. vendor jQUery
        if MARTOR_ALTERNATIVE_JQUERY_JS_FILE:
            js = (MARTOR_ALTERNATIVE_JQUERY_JS_FILE,) + js
        elif MARTOR_ENABLE_CONFIGS.get("jquery") == "true":
            js = ("plugins/js/jquery.min.js",) + js
