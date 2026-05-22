import logging

from django.shortcuts import render
from ..models import APIRequest, GeneratedSite
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import UserProfileForm, AccountForm
from ..models import UserProfile

from django.contrib.auth import update_session_auth_hash
from django.utils import translation


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

    llm_form     = UserProfileForm(instance=profile_obj)
    account_form = AccountForm(initial={
        "username":            request.user.username,
        "email":               request.user.email,
        "preferred_language":  profile_obj.preferred_language,
    })

    active_tab = "account"

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # ── ACCOUNT FORM ────────────────────────────────────────────
        if form_type == "account":
            active_tab   = "account"
            account_form = AccountForm(request.POST)

            if account_form.is_valid():
                cd = account_form.cleaned_data

                # Username
                new_username = cd["username"]
                if new_username != request.user.username:
                    if User.objects.filter(username=new_username).exclude(pk=request.user.pk).exists():
                        account_form.add_error("username", "Ese nombre de usuario ya está en uso.")
                    else:
                        request.user.username = new_username

                # Email
                request.user.email = cd["email"]
                request.user.save()

                # Idioma
                profile_obj.preferred_language = cd["preferred_language"]
                profile_obj.save(update_fields=["preferred_language"])

                # Activar idioma en sesión
                translation.activate(cd["preferred_language"])
                request.session[translation.LANGUAGE_SESSION_KEY] = cd["preferred_language"]

                # Contraseña
                current_pw = cd.get("current_password")
                new_pw     = cd.get("new_password")
                if new_pw and current_pw:
                    if not request.user.check_password(current_pw):
                        account_form.add_error("current_password", "Contraseña actual incorrecta.")
                    else:
                        request.user.set_password(new_pw)
                        request.user.save()
                        update_session_auth_hash(request, request.user)
                        messages.success(request, "Contraseña actualizada")

                if not account_form.errors:
                    messages.success(request, "Cuenta actualizada correctamente")

        # ── LLM FORM ────────────────────────────────────────────────
        elif form_type == "llm":
            active_tab = "llm"
            llm_form   = UserProfileForm(request.POST, instance=profile_obj)

            if llm_form.is_valid():
                llm_form.save()
                messages.success(request, "Modelo LLM guardado correctamente")
            else:
                messages.error(request, "Revisa los datos del modelo LLM.")

    return render(request, "WebBuilder/profile.html", {
        "account_form": account_form,
        "llm_form":     llm_form,
        "active_tab":   active_tab,
    })