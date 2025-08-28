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
    Класс с доступом изменений только автору, модератору, администратору.

    Параметры:
    - request (Request): HTTP-запрос, полученный сервером.
    - view (View): Viewset, в рамках которого запрашиваются права доступа.
    - obj (object): Объект модели, к которому применяются права доступа.
    Возвращаемое значение: bool.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return request.method in SAFE_METHODS or (
            obj.author == user
            or user.is_admin()
            or user.is_moderator
        )
