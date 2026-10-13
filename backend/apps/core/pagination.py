from rest_framework.pagination import CursorPagination, PageNumberPagination


class DefaultCursorPagination(CursorPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = "page_size"
    ordering = "-created_at"


class DefaultPageNumberPagination(PageNumberPagination):
    """Pour les listes triées par un calcul (ex. distance) : la pagination par
    curseur imposerait son propre ordre (`-created_at`) et casserait ce tri."""
    page_size = 20
    max_page_size = 100
    page_size_query_param = "page_size"
