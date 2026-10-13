from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Exists, OuterRef, QuerySet

from apps.core.exceptions import NotFound
from .models import Favorite, HousingListing, ListingStatus


def search_listings(
    *, user=None, center: Point | None = None, radius_m: int = 5000,
    min_rent=None, max_rent=None, room_types: list[str] | None = None,
    available_from=None, query: str | None = None,
) -> QuerySet[HousingListing]:
    qs = HousingListing.objects.filter(status=ListingStatus.ACTIVE)

    # ---- ÉTAPE 1 : filtre géographique via l'index GiST ----
    if center is not None:
        qs = qs.filter(location__dwithin=(center, D(m=radius_m)))
        qs = qs.annotate(distance=Distance("location", center))

    # ---- ÉTAPE 2 : filtres scalaires ----
    if min_rent is not None:
        qs = qs.filter(rent__gte=min_rent)
    if max_rent is not None:
        qs = qs.filter(rent__lte=max_rent)
    if room_types:
        qs = qs.filter(room_type__in=room_types)
    if available_from is not None:
        qs = qs.filter(available_from__lte=available_from)
    if query:
        qs = qs.filter(title__icontains=query)

    # ---- ÉTAPE 3 : éviter les N+1 ----
    qs = qs.select_related("owner").prefetch_related("photos")

    # ---- ÉTAPE 4 : "est-ce un favori ?" en UNE requête ----
    qs = _with_favorite_flag(qs, user)

    # "pk" en second critère : ordre stable même à distance / date égale.
    if center is not None:
        return qs.order_by("distance", "pk")
    return qs.order_by("-created_at", "-pk")


def listing_id_from_public_id(*, public_id) -> int:
    """L'API n'expose que `public_id` ; les services travaillent avec la clé interne."""
    pk = (HousingListing.objects.filter(public_id=public_id)
          .values_list("pk", flat=True).first())
    if pk is None:
        raise NotFound("Annonce introuvable.")
    return pk


def contact_visible_for(*, user, listing) -> bool:
    """Qui voit l'adresse exacte, le point GPS précis et le téléphone.
    PHASE 6 : le propriétaire seulement.
    PHASE 7.3 : remplacer par ports.call("housing.contact_visible", ...)
    pour l'ouvrir aussi aux étudiants dont la demande est acceptée."""
    return bool(user and user.is_authenticated and listing.owner_id == user.id)


def _with_favorite_flag(qs, user):
    if user is not None and user.is_authenticated:
        qs = qs.annotate(is_favorited=Exists(
            Favorite.objects.filter(user=user, listing=OuterRef("pk"))))
    return qs


def listing_detail(*, public_id, user=None) -> HousingListing:
    """Une annonce non active n'est visible que par son propriétaire (ou un modérateur)."""
    qs = (HousingListing.objects.filter(public_id=public_id)
          .select_related("owner").prefetch_related("photos"))
    listing = _with_favorite_flag(qs, user).first()
    if listing is None:
        raise NotFound("Annonce introuvable.")
    is_owner = user is not None and user.is_authenticated and (
        listing.owner_id == user.id or user.is_moderator)
    if listing.status != ListingStatus.ACTIVE and not is_owner:
        raise NotFound("Annonce introuvable.")
    return listing


def owner_listings(*, user) -> QuerySet[HousingListing]:
    """Toutes les annonces d'un propriétaire, quel que soit leur statut."""
    return (HousingListing.objects.filter(owner=user)
            .prefetch_related("photos").order_by("-created_at"))


def favorite_listings(*, user) -> QuerySet[HousingListing]:
    qs = (HousingListing.objects
          .filter(favorited_by__user=user, status=ListingStatus.ACTIVE)
          .select_related("owner").prefetch_related("photos")
          .order_by("-favorited_by__created_at"))
    return _with_favorite_flag(qs, user)
