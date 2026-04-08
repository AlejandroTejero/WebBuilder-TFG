"""Registro de ejemplos HTML por tipo de sitio."""

from .blog import BLOG_DETAIL_EXAMPLE, BLOG_HOME_EXAMPLE, BLOG_LIST_EXAMPLE
from .catalog import (
    CATALOG_DETAIL_EXAMPLE,
    CATALOG_HOME_EXAMPLE,
    CATALOG_LIST_EXAMPLE,
)
from .dashboard import DASHBOARD_HOME_EXAMPLE, DASHBOARD_LIST_EXAMPLE
from .portfolio import (
    PORTFOLIO_DETAIL_EXAMPLE,
    PORTFOLIO_HOME_EXAMPLE,
    PORTFOLIO_LIST_EXAMPLE,
)

EXAMPLES_BY_TYPE = {
    'catalog':   {'home': CATALOG_HOME_EXAMPLE,   'list': CATALOG_LIST_EXAMPLE,   'detail': CATALOG_DETAIL_EXAMPLE},
    'blog':      {'home': BLOG_HOME_EXAMPLE,       'list': BLOG_LIST_EXAMPLE,      'detail': BLOG_DETAIL_EXAMPLE},
    'portfolio': {'home': PORTFOLIO_HOME_EXAMPLE,  'list': PORTFOLIO_LIST_EXAMPLE, 'detail': PORTFOLIO_DETAIL_EXAMPLE},
    'dashboard': {'home': DASHBOARD_HOME_EXAMPLE,  'list': DASHBOARD_LIST_EXAMPLE},
}


def get_example(site_type: str, page_kind: str) -> str | None:
    return EXAMPLES_BY_TYPE.get(site_type, {}).get(page_kind)
