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
    """
    Сериализер для модели пользователя.
    Просмотр/редактирование профилей
    """
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве username'
            )
        return value


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для администратора.
    Админ может создавать пользователей и назначать им роль.
    """
    role = serializers.ChoiceField(
        choices=[
            ('user', 'user'),
            ('moderator', 'moderator'),
            ('admin', 'admin')
        ],
        required=False
    )
    first_name = serializers.CharField(
        required=False,
        max_length=150,
        allow_blank=True,
        default=''
    )
    last_name = serializers.CharField(
        required=False,
        max_length=150,
        allow_blank=True,
        default=''
    )
    bio = serializers.CharField(
        required=False,
        allow_blank=True,
        default=''
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве username'
            )
        return value

    def create(self, validated_data):
        # если роль не передана → user
        if 'role' not in validated_data:
            validated_data['role'] = 'user'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and not request.user.is_admin():
            validated_data.pop('role', None)
        return super().update(instance, validated_data)
