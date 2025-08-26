from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Чтение всем, изменения только администратору.
    """
    def has_permission(self, request, view):
        user = request.user
        return request.method in SAFE_METHODS or (
            user.is_authenticated and (
                getattr(user, 'role', None) == 'admin'
                or getattr(user, 'is_staff', False)
                or getattr(user, 'is_superuser', False)
            ))


class IsAuthorAdminModeratorOrReadOnly(BasePermission):
    """
    Изменения только автору, модератору, администратору.
    Остальным безопасные методы.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        return request.method in SAFE_METHODS or (
            obj.author == user
            or getattr(user, 'role', None) == 'admin'
            or getattr(user, 'role', None) == 'moderator'
            or getattr(user, 'role', None) == 'superuser'
        )
