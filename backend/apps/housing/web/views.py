"""Pages HTML provisoires des annonces (démo / validation).

Mêmes selectors et services que l'API : à supprimer quand le front Flutter
prend le relais, sans rien toucher d'autre.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from apps.core.exceptions import ApplicationError, NotFound
from apps.housing import selectors, services
from apps.housing.models import ListingStatus
from .forms import ListingForm, SearchForm


def _detail_or_404(public_id, user):
    try:
        return selectors.listing_detail(public_id=public_id, user=user)
    except NotFound:
        raise Http404 from None


def _back(request, default):
    nxt = request.POST.get("next")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return redirect(nxt)
    return redirect(default)


def listing_list(request):
    form = SearchForm(request.GET or None)
    filters = {}
    if form.is_valid():
        d = form.cleaned_data
        filters = {
            "query": d["q"] or None,
            "room_types": [d["room_type"]] if d["room_type"] else None,
            "min_rent": d["min_rent"],
            "max_rent": d["max_rent"],
        }
        if d["campus"]:
            filters["center"] = d["campus"].location
            filters["radius_m"] = (d["radius"] or 5) * 1000

    qs = selectors.search_listings(user=request.user, **filters)
    page = Paginator(qs, 12).get_page(request.GET.get("page"))

    # Conserve les filtres dans les liens de pagination.
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "housing/list.html", {
        "form": form, "page": page, "querystring": params.urlencode(),
        "geo_search": "center" in filters,
    })


def listing_detail(request, public_id):
    listing = _detail_or_404(public_id, request.user)
    visible = selectors.contact_visible_for(user=request.user, listing=listing)
    point = listing.location if visible else listing.blurred_location
    return render(request, "housing/detail.html", {
        "listing": listing, "visible": visible,
        "lat": point.y, "lon": point.x,
        "is_owner": request.user.is_authenticated and listing.owner_id == request.user.id,
        "statuses": ListingStatus,
    })


@login_required
@require_http_methods(["GET", "POST"])
def listing_create(request):
    form = ListingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        photo_urls = data.pop("photo_urls")
        try:
            listing = services.create_listing(owner=request.user, **data)
        except ApplicationError as e:
            form.add_error(None, e.message)
        except ValidationError as e:                # full_clean() du modèle
            for field, errs in e.message_dict.items():
                form.add_error(field if field in form.fields else None, errs)
        else:
            if photo_urls:
                services.add_photos(listing=listing, urls=photo_urls)
            messages.success(request, "Ton annonce est publiée.")
            return redirect("listings:detail", public_id=listing.public_id)
    return render(request, "housing/form.html", {"form": form})


@login_required
def my_listings(request):
    return render(request, "housing/my_listings.html", {
        "listings": selectors.owner_listings(user=request.user),
        "statuses": ListingStatus,
    })


@login_required
def favorites(request):
    return render(request, "housing/favorites.html", {
        "listings": selectors.favorite_listings(user=request.user),
    })


@login_required
@require_POST
def change_status(request, public_id):
    try:
        services.set_listing_status(
            user=request.user,
            listing_id=selectors.listing_id_from_public_id(public_id=public_id),
            new_status=request.POST.get("status", ""),
        )
    except NotFound:
        raise Http404 from None
    except ApplicationError as e:
        messages.error(request, e.message)
    else:
        messages.success(request, "Statut de l'annonce mis à jour.")
    return _back(request, "listings:mine")


@login_required
@require_POST
def toggle_favorite(request, public_id):
    try:
        added = services.toggle_favorite(
            user=request.user,
            listing_id=selectors.listing_id_from_public_id(public_id=public_id),
        )
    except NotFound:
        raise Http404 from None
    messages.success(request, "Ajoutée à tes favoris." if added else "Retirée de tes favoris.")
    return _back(request, "listings:favorites")
