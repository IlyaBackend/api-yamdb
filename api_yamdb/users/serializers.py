from rest_framework import serializers
from .models import CustomUser


class UserSignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    Принимает только username и email
    """
    username = serializers.RegexField(
        r'^[\w.@+-]+\Z',
        required=True,
        max_length=150,
        validators=[]
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[]
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        if username == 'me':
            raise serializers.ValidationError({
                'username': 'Недопуститмый username'
            })
        user_by_username = CustomUser.objects.filter(username=username).first()
        user_by_email = CustomUser.objects.filter(email=email).first()
        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError({
                'username': 'username занят другим пользователем'
            })
        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError({
                'email': 'email занят другим пользователем'
            })
        return attrs


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
