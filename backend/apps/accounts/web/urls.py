from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("", views.home, name="home"),
    path("inscription/", views.register, name="register"),
    path("connexion/", auth_views.LoginView.as_view(
        template_name="accounts/login.html", redirect_authenticated_user=True),
        name="login"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    path("profil/", views.profile, name="profile"),
    path("profil/supprimer/", views.delete_account, name="delete_account"),
]
