from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from apps.accounts.models import User, Campus


class CampusSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Campus
        fields = ("id", "name", "university", "address", "latitude", "longitude")

    def get_latitude(self, obj):
        return obj.location.y     # ⚠️ y = latitude

    def get_longitude(self, obj):
        return obj.location.x     # ⚠️ x = longitude


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    university = serializers.CharField(max_length=200, required=False, allow_blank=True)
    campus_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse est déjà utilisée.")
        return value


class MeSerializer(serializers.ModelSerializer):
    campus = CampusSerializer(read_only=True)
    # Sans ce champ, le campus serait IMPOSSIBLE à modifier : `campus` est
    # read_only (c'est un objet imbriqué), donc absent de validated_data, donc
    # update_profile() ne le verrait jamais. On expose la clé en écriture.
    campus_id = serializers.PrimaryKeyRelatedField(
        source="campus", queryset=Campus.objects.all(),
        required=False, allow_null=True, write_only=True,
    )
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("public_id", "email", "first_name", "last_name", "full_name",
                  "phone", "profile_picture", "university", "field_of_study",
                  "campus", "campus_id", "role", "push_enabled", "created_at")
        read_only_fields = ("public_id", "email", "role", "created_at")


class PublicUserSerializer(serializers.ModelSerializer):
    """Vue d'un AUTRE utilisateur : ni email, ni téléphone."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("public_id", "first_name", "full_name", "profile_picture",
                  "university", "field_of_study")
