"""Login/logout HTTP adapters. Django owns the session lifecycle."""

from django.contrib.auth import login, logout
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST

from src.services.auth import InvalidCredentials, authenticate_user

from .forms import LoginForm
from .session import safe_return_path, wants_json

INVALID_CREDENTIALS_MESSAGE = "Adresse e-mail ou mot de passe incorrect."


@never_cache
@sensitive_post_parameters("password")
@csrf_protect
@require_POST
def sign_in(request: HttpRequest) -> HttpResponse:
    form = LoginForm(request.POST)
    destination = safe_return_path(request.POST.get("next", ""))
    user = None
    if form.is_valid():
        try:
            user = authenticate_user(
                form.cleaned_data["email"], form.cleaned_data["password"]
            )
        except InvalidCredentials:
            pass
    if user is None:
        if wants_json(request):
            return JsonResponse({"error": INVALID_CREDENTIALS_MESSAGE}, status=401)
        return render(
            request,
            "login.html",
            {
                "form": form,
                "next": destination,
                "error": INVALID_CREDENTIALS_MESSAGE,
            },
            status=401,
        )
    login(request, user)
    if wants_json(request):
        return JsonResponse({"redirect": destination})
    return redirect(destination)


@never_cache
@csrf_protect
@require_POST
def sign_out(request: HttpRequest) -> HttpResponse:
    logout(request)
    destination = reverse("login") + "?logged_out=1"
    if wants_json(request):
        return JsonResponse({"redirect": destination})
    return redirect(destination)
