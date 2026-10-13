from decimal import Decimal

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator
from django.db import models
from apps.core.models import TimeStampedModel, UUIDModel


class RoomType(models.TextChoices):
    PRIVATE_ROOM = "PRIVATE_ROOM", "Chambre privée"
    SHARED_ROOM = "SHARED_ROOM", "Chambre partagée"
    STUDIO = "STUDIO", "Studio"
    APARTMENT = "APARTMENT", "Appartement"


class ListingStatus(models.TextChoices):
    PENDING_APPROVAL = "PENDING_APPROVAL", "En attente de validation"
    ACTIVE = "ACTIVE", "Active"
    PAUSED = "PAUSED", "En pause"
    HIDDEN = "HIDDEN", "Masquée par la modération"
    CLOSED = "CLOSED", "Clôturée"


class HousingListing(TimeStampedModel, UUIDModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="listings")
    title = models.CharField(max_length=200)
    description = models.TextField()
    rent = models.DecimalField(max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(Decimal("0"))])
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    room_type = models.CharField(max_length=20, choices=RoomType.choices)

    # --- Localisation ---
    address = models.CharField(max_length=300)          # ⚠️ sensible : masqué
    neighbourhood = models.CharField(max_length=150)    # public
    location = gis_models.PointField(geography=True, srid=4326, db_index=True)

    available_from = models.DateField()
    rules = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ListingStatus.choices,
                              default=ListingStatus.ACTIVE, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "room_type", "rent"]),
            models.Index(fields=["status", "-created_at"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(rent__gte=0), name="listing_rent_positive"),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def blurred_location(self):
        """Point arrondi à ~300 m — tant que la demande n'est pas acceptée."""
        from django.contrib.gis.geos import Point
        return Point(round(self.location.x, 3), round(self.location.y, 3), srid=4326)


class ListingPhoto(TimeStampedModel):
    listing = models.ForeignKey(HousingListing, on_delete=models.CASCADE,
                                related_name="photos")
    url = models.URLField()
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position"]


class Favorite(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="favorites")
    listing = models.ForeignKey(HousingListing, on_delete=models.CASCADE,
                                related_name="favorited_by")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "listing"], name="uniq_favorite"),
        ]
