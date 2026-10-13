from django.contrib.gis.geos import Point
from django.db import transaction

from apps.core.exceptions import InvalidTransition, NotAllowed, NotFound
from .models import HousingListing, ListingPhoto, ListingStatus, Favorite


@transaction.atomic
def create_listing(*, owner, latitude: float, longitude: float, **data) -> HousingListing:
    listing = HousingListing(
        owner=owner,
        location=Point(longitude, latitude, srid=4326),   # ⚠️ (lon, lat) !
        **data,
    )
    listing.full_clean()
    listing.save()
    return listing


@transaction.atomic
def set_listing_status(*, user, listing_id: int, new_status: str) -> HousingListing:
    try:
        listing = HousingListing.objects.select_for_update().get(pk=listing_id)
    except HousingListing.DoesNotExist:
        raise NotFound("Annonce introuvable.") from None

    if listing.owner_id != user.id and not user.is_moderator:
        raise NotAllowed("Vous n'êtes pas propriétaire de cette annonce.")

    allowed = {
        ListingStatus.ACTIVE: {ListingStatus.PAUSED, ListingStatus.CLOSED},
        ListingStatus.PAUSED: {ListingStatus.ACTIVE, ListingStatus.CLOSED},
        ListingStatus.PENDING_APPROVAL: {ListingStatus.ACTIVE, ListingStatus.HIDDEN},
        ListingStatus.HIDDEN: {ListingStatus.ACTIVE, ListingStatus.CLOSED},
        ListingStatus.CLOSED: set(),          # état terminal
    }

    if new_status not in allowed[listing.status]:
        raise InvalidTransition(
            f"Transition {listing.status} → {new_status} interdite.",
            code="INVALID_LISTING_TRANSITION",
        )

    listing.status = new_status
    listing.save(update_fields=["status", "updated_at"])
    return listing


@transaction.atomic
def toggle_favorite(*, user, listing_id: int) -> bool:
    if not HousingListing.objects.filter(pk=listing_id, status=ListingStatus.ACTIVE).exists():
        raise NotFound("Annonce introuvable.")
    fav, created = Favorite.objects.get_or_create(user=user, listing_id=listing_id)
    if not created:
        fav.delete()
    return created


@transaction.atomic
def add_photos(*, listing: HousingListing, urls: list[str]) -> None:
    start = listing.photos.count()
    ListingPhoto.objects.bulk_create(
        ListingPhoto(listing=listing, url=url, position=start + i)
        for i, url in enumerate(urls)
    )
