import logging

from django.shortcuts import render
from ..models import APIRequest, GeneratedSite
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import UserProfileForm
from ..models import UserProfile


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


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil guardado correctamente ✅")
        else:
            messages.error(request, "Revisa los datos introducidos.")
    else:
        form = UserProfileForm(instance=profile_obj)

    return render(request, "WebBuilder/profile.html", {"form": form})