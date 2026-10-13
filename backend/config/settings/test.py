from .base import *  # noqa: F403

DEBUG = False

# Hachage volontairement rapide : Argon2 ajoute ~300 ms PAR utilisateur créé.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
