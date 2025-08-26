from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Доступ только для администраторов (роль admin или superuser/staff).
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_admin()
        )
