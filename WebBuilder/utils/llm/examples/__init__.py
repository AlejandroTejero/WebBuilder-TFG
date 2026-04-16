# -*- coding: utf-8 -*-
"""Registro de ejemplos HTML por tipo de sitio y estilo visual."""

from .catalog import (
    CATALOG_HOME_DARK, CATALOG_HOME_LIGHT, CATALOG_HOME_EDITORIAL,
    CATALOG_LIST_DARK, CATALOG_LIST_LIGHT, CATALOG_LIST_EDITORIAL,
    CATALOG_DETAIL_DARK, CATALOG_DETAIL_LIGHT, CATALOG_DETAIL_EDITORIAL,
)
from .blog import (
    BLOG_HOME_DARK, BLOG_HOME_LIGHT, BLOG_HOME_EDITORIAL,
    BLOG_LIST_DARK, BLOG_LIST_LIGHT, BLOG_LIST_EDITORIAL,
    BLOG_DETAIL_DARK, BLOG_DETAIL_LIGHT, BLOG_DETAIL_EDITORIAL,
)
from .portfolio import (
    PORTFOLIO_HOME_DARK, PORTFOLIO_HOME_LIGHT, PORTFOLIO_HOME_EDITORIAL,
    PORTFOLIO_LIST_DARK, PORTFOLIO_LIST_LIGHT, PORTFOLIO_LIST_EDITORIAL,
    PORTFOLIO_DETAIL_DARK, PORTFOLIO_DETAIL_LIGHT, PORTFOLIO_DETAIL_EDITORIAL,
)
from .dashboard import (
    DASHBOARD_HOME_DARK, DASHBOARD_HOME_LIGHT, DASHBOARD_HOME_EDITORIAL,
    DASHBOARD_LIST_DARK, DASHBOARD_LIST_LIGHT, DASHBOARD_LIST_EDITORIAL,
    DASHBOARD_DETAIL_DARK, DASHBOARD_DETAIL_LIGHT, DASHBOARD_DETAIL_EDITORIAL,
)

_DARK_WORDS = {"dark", "night", "black", "moody", "bold", "dramatic"}
_LIGHT_WORDS = {"light", "clean", "minimal", "white", "simple", "bright", "airy"}
_EDITORIAL_WORDS = {"editorial", "magazine", "newspaper", "sober", "text", "reading", "literary"}


def _detect_style(user_prompt: str) -> str:
    words = set(user_prompt.lower().split())
    if words & _EDITORIAL_WORDS:
        return "editorial"
    if words & _LIGHT_WORDS:
        return "light"
    if words & _DARK_WORDS:
        return "dark"
    return "light"


EXAMPLES_BY_TYPE = {
    "catalog": {
        "home":   {"dark": CATALOG_HOME_DARK,   "light": CATALOG_HOME_LIGHT,   "editorial": CATALOG_HOME_EDITORIAL},
        "list":   {"dark": CATALOG_LIST_DARK,   "light": CATALOG_LIST_LIGHT,   "editorial": CATALOG_LIST_EDITORIAL},
        "detail": {"dark": CATALOG_DETAIL_DARK, "light": CATALOG_DETAIL_LIGHT, "editorial": CATALOG_DETAIL_EDITORIAL},
    },
    "blog": {
        "home":   {"dark": BLOG_HOME_DARK,   "light": BLOG_HOME_LIGHT,   "editorial": BLOG_HOME_EDITORIAL},
        "list":   {"dark": BLOG_LIST_DARK,   "light": BLOG_LIST_LIGHT,   "editorial": BLOG_LIST_EDITORIAL},
        "detail": {"dark": BLOG_DETAIL_DARK, "light": BLOG_DETAIL_LIGHT, "editorial": BLOG_DETAIL_EDITORIAL},
    },
    "portfolio": {
        "home":   {"dark": PORTFOLIO_HOME_DARK,   "light": PORTFOLIO_HOME_LIGHT,   "editorial": PORTFOLIO_HOME_EDITORIAL},
        "list":   {"dark": PORTFOLIO_LIST_DARK,   "light": PORTFOLIO_LIST_LIGHT,   "editorial": PORTFOLIO_LIST_EDITORIAL},
        "detail": {"dark": PORTFOLIO_DETAIL_DARK, "light": PORTFOLIO_DETAIL_LIGHT, "editorial": PORTFOLIO_DETAIL_EDITORIAL},
    },
    "dashboard": {
        "home":   {"dark": DASHBOARD_HOME_DARK,   "light": DASHBOARD_HOME_LIGHT,   "editorial": DASHBOARD_HOME_EDITORIAL},
        "list":   {"dark": DASHBOARD_LIST_DARK,   "light": DASHBOARD_LIST_LIGHT,   "editorial": DASHBOARD_LIST_EDITORIAL},
        "detail": {"dark": DASHBOARD_DETAIL_DARK, "light": DASHBOARD_DETAIL_LIGHT, "editorial": DASHBOARD_DETAIL_EDITORIAL},
    },
}


def get_example(site_type: str, page_kind: str, user_prompt: str = "") -> str | None:
    style = _detect_style(user_prompt)
    return EXAMPLES_BY_TYPE.get(site_type, {}).get(page_kind, {}).get(style)