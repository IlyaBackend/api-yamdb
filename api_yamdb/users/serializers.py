from rest_framework import serializers
from .models import CustomUser


class UserSignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    Принимает только username и email
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class UserSerializer(serializers.ModelSerializer):
    '''
    Сериализер для модели пользователя.
    Просмотр/редактирование профилей
    '''
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class AdminUserSerializer(serializers.ModelSerializer):
    '''
    Сериализер для администратора.
    Администратор может просматривать и изменять роль пользователя
    '''
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
