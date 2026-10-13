from django import forms
from django.core.validators import URLValidator

from apps.accounts.models import Campus
from apps.housing.models import HousingListing, RoomType


class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)

    q = forms.CharField(label="Recherche", required=False,
                        widget=forms.TextInput(attrs={"placeholder": "Studio, chambre…"}))
    room_type = forms.ChoiceField(label="Type", required=False,
                                  choices=[("", "Tous")] + RoomType.choices)
    min_rent = forms.DecimalField(label="Loyer min", required=False, min_value=0)
    max_rent = forms.DecimalField(label="Loyer max", required=False, min_value=0)
    campus = forms.ModelChoiceField(label="Près du campus", queryset=Campus.objects.all(),
                                    required=False, empty_label="Partout")
    radius = forms.TypedChoiceField(label="Rayon", coerce=int, initial=5, required=False,
                                    choices=[(1, "1 km"), (3, "3 km"), (5, "5 km"),
                                             (10, "10 km"), (20, "20 km"), (50, "50 km")])


class ListingForm(forms.ModelForm):
    # Pas des champs du modèle : services.create_listing() fabrique le Point.
    latitude = forms.FloatField(label="Latitude", min_value=-90, max_value=90,
                                widget=forms.NumberInput(attrs={"step": "any"}))
    longitude = forms.FloatField(label="Longitude", min_value=-180, max_value=180,
                                 widget=forms.NumberInput(attrs={"step": "any"}))
    photo_urls = forms.CharField(
        label="Photos (une URL par ligne)", required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "https://…/photo1.jpg"}))

    class Meta:
        model = HousingListing
        fields = ("title", "description", "room_type", "rent", "deposit",
                  "available_from", "neighbourhood", "address", "rules")
        labels = {
            "title": "Titre", "description": "Description", "room_type": "Type de logement",
            "rent": "Loyer mensuel (DT)", "deposit": "Caution (DT)",
            "available_from": "Disponible à partir du", "neighbourhood": "Quartier (public)",
            "address": "Adresse exacte (privée)", "rules": "Règles de la maison",
        }
        help_texts = {
            "address": "Visible uniquement par toi tant qu'aucune demande n'est acceptée.",
            "neighbourhood": "Ex. « Ariana, près de la fac » — affiché à tout le monde.",
        }
        widgets = {
            "available_from": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
            "rules": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_photo_urls(self):
        urls = [u.strip() for u in self.cleaned_data["photo_urls"].splitlines() if u.strip()]
        validate = URLValidator()
        for url in urls:
            try:
                validate(url)
            except forms.ValidationError:
                raise forms.ValidationError(f"URL invalide : {url}") from None
        return urls
