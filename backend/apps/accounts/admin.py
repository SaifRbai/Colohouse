from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import User, Campus, FCMDevice


@admin.register(Campus)
class CampusAdmin(GISModelAdmin):
    list_display = ("name", "university", "address")
    search_fields = ("name", "university")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "role", "campus",
                    "is_suspended", "is_active", "created_at")
    list_filter = ("role", "is_suspended", "is_active")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("public_id", "last_login", "created_at", "updated_at")
    exclude = ("password",)


@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "created_at")
