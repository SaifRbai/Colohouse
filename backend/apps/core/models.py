import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """Horodatage de création et de modification, hérité par tous les modèles."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Identifiant public non devinable, en plus de la clé primaire entière."""
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        abstract = True
