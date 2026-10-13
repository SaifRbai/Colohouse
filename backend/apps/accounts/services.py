from django.db import transaction
from .models import User, FCMDevice


@transaction.atomic
def register_user(*, email: str, password: str, first_name: str,
                  last_name: str, **extra) -> User:
    return User.objects.create_user(
        email=email.lower().strip(), password=password,
        first_name=first_name, last_name=last_name, **extra,
    )


@transaction.atomic
def update_profile(*, user: User, **fields) -> User:
    allowed = {"first_name", "last_name", "phone", "university",
               "field_of_study", "campus", "push_enabled", "profile_picture"}
    for key, value in fields.items():
        if key in allowed:
            setattr(user, key, value)
    user.full_clean(exclude=["password"])
    user.save()
    return user


@transaction.atomic
def delete_account(*, user: User) -> None:
    """RGPD : anonymiser au lieu de supprimer."""
    user.email = f"deleted_{user.public_id}@colohouse.invalid"
    user.first_name, user.last_name = "Utilisateur", "supprimé"
    user.phone = ""
    user.profile_picture = ""
    user.is_active = False
    user.set_unusable_password()
    user.save()
    user.devices.all().delete()


@transaction.atomic
def register_device(*, user: User, token: str) -> FCMDevice:
    device, _ = FCMDevice.objects.update_or_create(
        token=token, defaults={"user": user, "is_active": True},
    )
    return device
