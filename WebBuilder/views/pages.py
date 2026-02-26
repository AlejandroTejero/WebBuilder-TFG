import logging

from django.shortcuts import render

from ..models import APIRequest, GeneratedSite

logger = logging.getLogger(__name__)


def home(request):
    try:
        context = {}

        if request.user.is_authenticated:
            context["recent_requests"] = (
                APIRequest.objects
                .filter(user=request.user)
                .order_by("-date")[:3]
            )
            context["recent_sites"] = (
                GeneratedSite.objects
                .filter(project_source__user=request.user)
                .select_related("project_source")
                .order_by("-created_at")[:3]
            )

        return render(request, "WebBuilder/home.html", context)

    except Exception as exc:
        logger.exception("Error en home: %s", exc)
        return render(request, "WebBuilder/home.html", {})