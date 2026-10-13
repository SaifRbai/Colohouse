from django.contrib.gis.geos import Point
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from apps.core.pagination import DefaultPageNumberPagination
from apps.housing import selectors, services
from apps.housing.models import ListingStatus
from .serializers import ListingDetailSerializer, ListingListSerializer, ListingWriteSerializer


class SearchParamsSerializer(serializers.Serializer):
    """Valide la query string : une valeur absurde donne un 400 lisible, pas une 500."""
    lat = serializers.FloatField(min_value=-90, max_value=90, required=False)
    lon = serializers.FloatField(min_value=-180, max_value=180, required=False)
    radius = serializers.IntegerField(min_value=100, max_value=50_000, default=5000)
    min_rent = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_rent = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    available_from = serializers.DateField(required=False)
    q = serializers.CharField(required=False, allow_blank=True)


class ListingViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    # Le client ne connaît que public_id (l'id interne n'est jamais exposé).
    lookup_field = "public_id"
    lookup_value_regex = r"[0-9a-fA-F-]{36}"
    # Tri par distance : la pagination par curseur l'écraserait par -created_at.
    pagination_class = DefaultPageNumberPagination

    # ⚠️ OBLIGATOIRE : RetrieveModelMixin appelle get_serializer(), qui lève
    # une AssertionError si ni serializer_class ni get_serializer_class n'existe.
    def get_serializer_class(self):
        if self.action == "list":
            return ListingListSerializer
        if self.action == "create":
            return ListingWriteSerializer
        return ListingDetailSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        if self.action != "list":
            return selectors.search_listings(user=self.request.user)

        p = SearchParamsSerializer(data=self.request.query_params)
        p.is_valid(raise_exception=True)
        p = p.validated_data
        center = None
        if "lat" in p and "lon" in p:
            center = Point(p["lon"], p["lat"], srid=4326)      # ⚠️ (lon, lat) !
        return selectors.search_listings(
            user=self.request.user,
            center=center,
            radius_m=p["radius"],
            min_rent=p.get("min_rent"),
            max_rent=p.get("max_rent"),
            room_types=self.request.query_params.getlist("room_type") or None,
            available_from=p.get("available_from"),
            query=p.get("q"),
        )

    def list(self, request):
        page = self.paginate_queryset(self.get_queryset())
        return self.get_paginated_response(
            ListingListSerializer(page, many=True, context={"request": request}).data
        )

    def create(self, request):
        s = ListingWriteSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        listing = services.create_listing(owner=request.user, **s.validated_data)
        return Response(ListingDetailSerializer(listing, context={"request": request}).data,
                        status=status.HTTP_201_CREATED)

    def _set_status(self, request, public_id, new_status):
        listing = services.set_listing_status(
            user=request.user,
            listing_id=selectors.listing_id_from_public_id(public_id=public_id),
            new_status=new_status,
        )
        return Response(ListingDetailSerializer(listing, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def pause(self, request, public_id=None):
        return self._set_status(request, public_id, ListingStatus.PAUSED)

    @action(detail=True, methods=["post"])
    def resume(self, request, public_id=None):
        return self._set_status(request, public_id, ListingStatus.ACTIVE)

    @action(detail=True, methods=["post"])
    def close(self, request, public_id=None):
        return self._set_status(request, public_id, ListingStatus.CLOSED)

    @action(detail=True, methods=["post"])
    def favorite(self, request, public_id=None):
        created = services.toggle_favorite(
            user=request.user,
            listing_id=selectors.listing_id_from_public_id(public_id=public_id),
        )
        return Response({"favorited": created})
