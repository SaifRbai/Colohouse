"""Registre de ports nommés : permet à une app BASSE d'appeler une app HAUTE
sans l'importer, donc sans créer de cycle de dépendances."""

from typing import Callable

_ports: dict[str, Callable] = {}


class PortNotProvided(RuntimeError):
    pass


def provide(name: str):
    """Décorateur : l'app qui IMPLÉMENTE le port s'enregistre ici (dans AppConfig.ready)."""
    def decorator(fn: Callable):
        _ports[name] = fn
        return fn
    return decorator


def call(name: str, **kwargs):
    """Appelle le port. Lève si personne ne l'a fourni — jamais de silence."""
    try:
        fn = _ports[name]
    except KeyError:
        raise PortNotProvided(
            f"Port '{name}' non fourni. L'app qui l'implémente est-elle dans "
            f"INSTALLED_APPS, et son AppConfig.ready() importe-t-il bien son module ?"
        ) from None
    return fn(**kwargs)
