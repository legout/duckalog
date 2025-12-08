"""Dashboard components package."""

from .base import (
    page,
    card,
    alert,
    loading_spinner,
    breadcrumb,
    button,
    form_input,
    form_textarea,
)

from .forms import (
    query_form,
    build_form,
    view_search_form,
    export_form,
    config_form,
    filter_form,
)

from .navigation import (
    sidebar,
    header,
    footer,
    tab_navigation,
    action_bar,
    quick_links,
    back_button,
    view_navigation,
    semantic_model_navigation,
)

from .tables import (
    data_table,
    view_table,
    query_results_table,
    search_form,
    pagination_info,
    status_badge,
)

__all__ = [
    # Base components
    "page",
    "card",
    "alert",
    "loading_spinner",
    "breadcrumb",
    "button",
    "form_input",
    "form_textarea",

    # Form components
    "query_form",
    "build_form",
    "view_search_form",
    "export_form",
    "config_form",
    "filter_form",

    # Navigation components
    "sidebar",
    "header",
    "footer",
    "tab_navigation",
    "action_bar",
    "quick_links",
    "back_button",
    "view_navigation",
    "semantic_model_navigation",

    # Table components
    "data_table",
    "view_table",
    "query_results_table",
    "search_form",
    "pagination_info",
    "status_badge",
]