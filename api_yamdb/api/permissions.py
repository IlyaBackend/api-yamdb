from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    '''
    Чтение всем, изменения только администратору.
    '''
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return (
            user.is_authenticated and (
                getattr(user, 'role', None) == 'admin'
                or getattr(user, 'is_staff', False)
                or getattr(user, 'is_superuser', False)
            )
        )


class IsAuthorAdminModeratorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Разрешаем GET, HEAD, OPTIONS запросы всем
        if request.method in SAFE_METHODS:
            return True
        # Разрешаем создание (POST) только аутентифицированным пользователям
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение для всех
        if request.method in SAFE_METHODS:
            return True
        # Разрешаем редактирование и удаление автору, модератору или админу
        return (
            obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
