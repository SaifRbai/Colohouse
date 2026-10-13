from django.contrib.gis.db.models.functions import Distance
from .models import Campus, User


def campus_list(*, search: str | None = None):
    qs = Campus.objects.all()
    if search:
        qs = qs.filter(name__icontains=search)
    return qs.order_by("university", "name")


def nearest_campuses(*, point, limit: int = 5):
    return (Campus.objects
            .annotate(distance=Distance("location", point))
            .order_by("distance")[:limit])


def user_detail(*, user_id: int) -> User:
    return User.objects.select_related("campus").get(pk=user_id)
