from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):

    """
    Доступ только для администраторов.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_admin()
        )


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
        )
