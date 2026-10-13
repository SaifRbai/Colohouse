from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.gis.db import models as gis_models
from django.db import models
from apps.core.models import TimeStampedModel, UUIDModel


class Role(models.TextChoices):
    STUDENT = "STUDENT", "Étudiant"
    MODERATOR = "MODERATOR", "Modérateur"
    ADMIN = "ADMIN", "Administrateur"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", Role.ADMIN)
        return self.create_user(email, password, **extra)


class Campus(TimeStampedModel):
    name = models.CharField(max_length=150)
    university = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    location = gis_models.PointField(geography=True, srid=4326, db_index=True)

    class Meta:
        verbose_name_plural = "campuses"
        constraints = [
            models.UniqueConstraint(fields=["name", "university"],
                                    name="uniq_campus_per_university"),
        ]

    def __str__(self):
        return f"{self.name} — {self.university}"


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, UUIDModel):
    # --- Identité ---
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True)       # ⚠️ donnée sensible
    profile_picture = models.URLField(blank=True)

    # --- Contexte étudiant ---
    university = models.CharField(max_length=200, blank=True)
    field_of_study = models.CharField(max_length=200, blank=True)
    campus = models.ForeignKey(Campus, null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="students")

    # --- Plateforme ---
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    is_suspended = models.BooleanField(default=False)
    suspended_until = models.DateTimeField(null=True, blank=True)

    # --- Notifications ---
    push_enabled = models.BooleanField(default=True)

    # --- Django ---
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        indexes = [models.Index(fields=["role", "is_suspended"])]

    def __str__(self):
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_moderator(self) -> bool:
        return self.role in (Role.MODERATOR, Role.ADMIN)


class FCMDevice(TimeStampedModel):
    """Un utilisateur peut avoir plusieurs appareils."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    token = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
