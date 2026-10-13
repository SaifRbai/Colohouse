"""Pages HTML provisoires (démo / validation).

Elles appellent les MÊMES services que l'API : le jour où le front Flutter
prend le relais, on supprime ce dossier `web/` et `templates/` sans rien
toucher d'autre.
"""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts import services
from .forms import RegisterForm, ProfileForm


def home(request):
    return render(request, "home.html")


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("web:profile")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        user = services.register_user(
            email=data["email"], password=data["password1"],
            first_name=data["first_name"], last_name=data["last_name"],
            university=data["university"], campus=data["campus"],
        )
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"Bienvenue {user.first_name}, ton compte est créé.")
        return redirect("web:profile")
    return render(request, "accounts/register.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        services.update_profile(user=request.user, **form.cleaned_data)
        messages.success(request, "Profil mis à jour.")
        return redirect("web:profile")
    return render(request, "accounts/profile.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def delete_account(request):
    if request.method == "POST":
        services.delete_account(user=request.user)
        logout(request)
        messages.info(request, "Ton compte a été supprimé.")
        return redirect("web:home")
    return render(request, "accounts/delete_account.html")
