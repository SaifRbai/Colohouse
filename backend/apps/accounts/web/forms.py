from django import forms
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import User, Campus


class RegisterForm(forms.Form):
    email = forms.EmailField(label="Adresse email")
    first_name = forms.CharField(label="Prénom", max_length=100)
    last_name = forms.CharField(label="Nom", max_length=100)
    university = forms.CharField(label="Université", max_length=200, required=False)
    campus = forms.ModelChoiceField(label="Campus", queryset=Campus.objects.all(),
                                    required=False, empty_label="— Aucun —")
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput)

    def clean_email(self):
        value = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email=value).exists():
            raise forms.ValidationError("Cette adresse est déjà utilisée.")
        return value

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Les deux mots de passe ne correspondent pas.")
        elif p1:
            # Même règles que l'API (AUTH_PASSWORD_VALIDATORS : 10 caractères min., etc.)
            user = User(email=data.get("email", ""), first_name=data.get("first_name", ""),
                        last_name=data.get("last_name", ""))
            try:
                validate_password(p1, user)
            except forms.ValidationError as e:
                self.add_error("password1", e)
        return data


class ProfileForm(forms.ModelForm):
    """Mêmes champs que ceux autorisés par services.update_profile()."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "university",
                  "field_of_study", "campus", "profile_picture", "push_enabled")
        labels = {
            "first_name": "Prénom", "last_name": "Nom", "phone": "Téléphone",
            "university": "Université", "field_of_study": "Filière",
            "campus": "Campus", "profile_picture": "Photo de profil (URL)",
            "push_enabled": "Recevoir les notifications",
        }
