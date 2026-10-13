from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import HousingListing, ListingPhoto, Favorite


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 1


@admin.register(HousingListing)
class HousingListingAdmin(GISModelAdmin):
    list_display = ("title", "owner", "room_type", "rent", "neighbourhood",
                    "status", "created_at")
    list_filter = ("status", "room_type")
    search_fields = ("title", "neighbourhood", "owner__email")
    readonly_fields = ("public_id", "created_at", "updated_at")
    inlines = [ListingPhotoInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "created_at")
