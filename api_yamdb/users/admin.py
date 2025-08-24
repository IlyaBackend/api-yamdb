# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser


# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
#     list_filter = ('role', 'is_staff', 'is_active')
#     search_fields = ('username', 'email')
#     ordering = ('id',)

#     fieldsets = (
#         (None, {'fields': ('username', 'email', 'password')}),
#         ('Персональная информация', {'fields': (
#         'first_name', 'last_name', 'bio')}),
#         ('Права доступа', {'fields': (
#             'role', 'is_staff', 'is_active', 'is_superuser'
#         )}),
#         ('Код подтверждения', {'fields': ('confirmation_code',)}),
#     )
