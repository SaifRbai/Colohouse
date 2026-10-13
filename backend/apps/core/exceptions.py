class ApplicationError(Exception):
    """Erreur métier attendue. Produit une réponse 4xx propre, jamais une 500."""

    default_code = "APPLICATION_ERROR"
    status_code = 400

    def __init__(self, message: str, *, code: str | None = None,
                 field_errors: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.default_code
        self.field_errors = field_errors or {}


class NotAllowed(ApplicationError):
    default_code = "NOT_ALLOWED"
    status_code = 403


class InvalidTransition(ApplicationError):
    """Transition d'état interdite : accepter une demande déjà refusée, etc."""
    default_code = "INVALID_TRANSITION"
    status_code = 409


class NotFound(ApplicationError):
    default_code = "NOT_FOUND"
    status_code = 404
