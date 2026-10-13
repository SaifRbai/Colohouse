import logging
from rest_framework.views import exception_handler as drf_handler
from rest_framework.response import Response
from rest_framework import exceptions as drf_exc
from .exceptions import ApplicationError

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    request = context.get("request")
    request_id = getattr(request, "request_id", None)

    if isinstance(exc, ApplicationError):
        return Response(
            {"error": {
                "code": exc.code,
                "message": exc.message,
                "field_errors": exc.field_errors,
                "request_id": request_id,
            }},
            status=exc.status_code,
        )

    response = drf_handler(exc, context)
    if response is None:
        logger.exception("Erreur non gérée", extra={"request_id": request_id})
        return Response(
            {"error": {"code": "INTERNAL_ERROR",
                       "message": "Une erreur interne est survenue.",
                       "field_errors": {},
                       "request_id": request_id}},
            status=500,
        )

    detail = response.data
    field_errors = detail if isinstance(detail, dict) and "detail" not in detail else {}
    message = detail.get("detail") if isinstance(detail, dict) else str(detail)

    response.data = {"error": {
        "code": _code_for(exc),
        "message": str(message or "Requête invalide."),
        "field_errors": field_errors,
        "request_id": request_id,
    }}
    return response


def _code_for(exc) -> str:
    return {
        drf_exc.NotAuthenticated: "NOT_AUTHENTICATED",
        drf_exc.AuthenticationFailed: "AUTHENTICATION_FAILED",
        drf_exc.PermissionDenied: "PERMISSION_DENIED",
        drf_exc.NotFound: "NOT_FOUND",
        drf_exc.Throttled: "RATE_LIMITED",
        drf_exc.ValidationError: "VALIDATION_ERROR",
    }.get(type(exc), "ERROR")
