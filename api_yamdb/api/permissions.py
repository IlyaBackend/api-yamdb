from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Чтение всем, изменения только администратору.
    """
    def has_permission(self, request, view):
        user = request.user
        return request.method in SAFE_METHODS or (
            user.is_authenticated and (
                user.role == 'admin'
                or user.is_staff
                or user.is_superuser
            ))


class IsAuthorAdminModeratorOrReadOnly(BasePermission):
    """
    Изменения только автору, модератору, администратору.
    Остальным безопасные методы.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        return request.method in SAFE_METHODS or (
            obj.author == user
            or user.role == 'admin'
            or user.role == 'moderator'
            or user.is_superuser
        )
