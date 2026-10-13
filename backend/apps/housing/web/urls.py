from django.urls import path
from . import views

app_name = "listings"

urlpatterns = [
    path("annonces/", views.listing_list, name="list"),
    path("annonces/publier/", views.listing_create, name="create"),
    path("annonces/<uuid:public_id>/", views.listing_detail, name="detail"),
    path("annonces/<uuid:public_id>/statut/", views.change_status, name="status"),
    path("annonces/<uuid:public_id>/favori/", views.toggle_favorite, name="favorite"),
    path("mes-annonces/", views.my_listings, name="mine"),
    path("favoris/", views.favorites, name="favorites"),
]
