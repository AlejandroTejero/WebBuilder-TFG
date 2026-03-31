from .auth import register
from .pages import home
from .assistant import assistant
from .history import history, history_analysis, history_sites, delete_analysis, delete_site
from .edit import edit
from .site import (
    site_render,
    site_generate,
    site_download_zip,
    site_status,
    site_deploy,
    site_deploy_status,
	site_update_file
)

__all__ = [
    "register",
    "home",
    "assistant",
    "history",
	"history_analysis",
    "history_sites",
    "edit",
    "site_render",
    "site_generate",
    "site_download_zip",
    "site_status",
    "site_deploy",
    "site_deploy_status",
	"site_update_file",
	"delete_analysis",
	"delete_site",
]
