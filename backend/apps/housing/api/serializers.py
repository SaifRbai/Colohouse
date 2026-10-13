from rest_framework import serializers

from apps.accounts.api.serializers import PublicUserSerializer
from apps.housing import selectors
from apps.housing.models import HousingListing, ListingPhoto


class ListingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPhoto
        fields = ("id", "url", "position")


class ListingWriteSerializer(serializers.ModelSerializer):
    # Le client envoie latitude/longitude ; le service fabrique le Point.
    latitude = serializers.FloatField(min_value=-90, max_value=90, write_only=True)
    longitude = serializers.FloatField(min_value=-180, max_value=180, write_only=True)

    class Meta:
        model = HousingListing
        fields = ("title", "description", "rent", "deposit", "room_type",
                  "address", "neighbourhood", "available_from", "rules",
                  "latitude", "longitude")


class ListingListSerializer(serializers.ModelSerializer):
    """Vue de liste : volontairement pauvre. Ni adresse, ni point précis."""
    owner = PublicUserSerializer(read_only=True)
    photos = ListingPhotoSerializer(many=True, read_only=True)
    distance_m = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = HousingListing
        fields = ("public_id", "title", "rent", "room_type", "neighbourhood",
                  "available_from", "owner", "photos", "distance_m",
                  "is_favorited", "created_at")

    def get_distance_m(self, obj) -> int | None:
        d = getattr(obj, "distance", None)      # annotation du sélecteur
        return round(d.m) if d is not None else None


class ListingDetailSerializer(serializers.ModelSerializer):
    owner = PublicUserSerializer(read_only=True)
    photos = ListingPhotoSerializer(many=True, read_only=True)
    location = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = HousingListing
        fields = ("public_id", "title", "description", "rent", "deposit",
                  "room_type", "neighbourhood", "location", "available_from",
                  "rules", "status", "owner", "photos", "contact",
                  "is_favorited", "created_at")
        # ⚠️ "address" N'EST PAS dans la liste : jamais sérialisé par défaut.

    def _visible(self, obj) -> bool:
        request = self.context.get("request")
        return selectors.contact_visible_for(user=getattr(request, "user", None), listing=obj)

    def get_location(self, obj) -> dict:
        visible = self._visible(obj)
        point = obj.location if visible else obj.blurred_location
        return {"latitude": point.y, "longitude": point.x, "precise": visible}

    def get_contact(self, obj) -> dict | None:
        if not self._visible(obj):
            return None          # la clé existe, la donnée n'existe pas
        return {"address": obj.address, "phone": obj.owner.phone}
