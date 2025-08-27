from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    """Доступ только для администраторов."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_admin()
        )


class IsAdminOrReadOnly(BasePermission):
    """Чтение всем, изменения только администратору."""

    def has_permission(self, request, view):
        user = request.user
        return (request.method in SAFE_METHODS
                or (user.is_authenticated and user.is_admin()))


class IsAuthorAdminModeratorOrReadOnly(BasePermission):
    """
    Обеспечивает доступ на изменение только автору или персоналу.

    Пользователи с правами автора, модератора или администратора
    имеют полный доступ к объекту.
    Остальным пользователям доступны только безопасные методы
    (GET, HEAD, OPTIONS)
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return request.method in SAFE_METHODS or (
            obj.author == user
            or user.is_admin()
            or user.is_moderator
            or user.is_superuser
        )
