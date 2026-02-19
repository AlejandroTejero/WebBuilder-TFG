from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required


@login_required
def preview(request, api_request_id: int):
    return HttpResponseNotFound("Preview desactivado temporalmente (pendiente de implementar LLM y mapping).")
