from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Доступ только для администраторов (роль admin или superuser/staff).
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_admin()
        )


# class IsAdminOrReadOnly(permissions.BasePermission):
#     """
#     Админ может редактировать, остальные — только читать.
#     """
#     def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return request.user.is_authenticated and request.user.is_admin()
