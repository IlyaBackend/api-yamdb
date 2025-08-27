from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api_yamdb.constants import (EMAIL_MAX_LENGTH, FIRST_NAME_MAX_LENGTH,
                                 LAST_NAME_MAX_LENGTH, MY_USER_PROFILE,
                                 REGULAR_USERNAME, USERNAME_MAX_LENGTH)
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSignUpSerializer(serializers.ModelSerializer):

    '''
    Сериализатор для регистрации нового пользователя.
    Принимает только username и email
    '''
    username = serializers.RegexField(
        REGULAR_USERNAME,
        required=True,
        max_length=USERNAME_MAX_LENGTH,
    )
    email = serializers.EmailField(
        required=True,
        max_length=EMAIL_MAX_LENGTH,
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        if username == MY_USER_PROFILE:
            raise serializers.ValidationError({
                'username': 'Недопуститмый username'
            })
        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()
        if (user_by_email and user_by_email.username != username) and (
            user_by_username and user_by_username.email != email
        ):
            raise serializers.ValidationError({
                'username': 'username занят другим пользователем',
                'email': 'email занят другим пользователем'
            })
        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError({
                'username': 'username занят другим пользователем'
            })
        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError({
                'email': 'email занят другим пользователем'
            })
        return attrs

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        return user


class AdminUserSerializer(serializers.ModelSerializer):

    '''
    Сериализатор для администратора.
    Админ может создавать пользователей и назначать им роль.
    '''
    first_name = serializers.CharField(
        required=False,
        max_length=FIRST_NAME_MAX_LENGTH,
        allow_blank=True,
        default=''
    )
    last_name = serializers.CharField(
        required=False,
        max_length=LAST_NAME_MAX_LENGTH,
        allow_blank=True,
        default=''
    )
    bio = serializers.CharField(
        required=False,
        allow_blank=True,
        default=''
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def update(self, instance, validated_data):
        if self.context.get('view') and self.context['view'].action == 'me':
            validated_data.pop('role', None)
        return super().update(instance, validated_data)


class TokenSerializer(serializers.Serializer):

    """
    Сериализатор для валидации username, confirmation_code
    и последующего создания токена.
    """
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True
    )
    confirmation_code = serializers.CharField(max_length=255, required=True)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        if not username or not confirmation_code:
            raise ValidationError(
                {'error': '"username" и "confirmation_code" обязательны'}
            )
        user = get_object_or_404(User, username=username)
        if not user.check_confirmation_code(confirmation_code):
            raise ValidationError(
                {'error': 'Код подтверждения неверен.'}
            )
        self.context['user'] = user
        return data


class CategorySerializer(serializers.ModelSerializer):

    """Сериализатор для категорий."""

    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):

    """Сериализатор для произведений."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        ]

    def get_rating(self, title):
        """
        Возвращает среднюю оценку произведения
        или сообщение об отсутствии отзывов.
        """
        avg_score = getattr(title, 'score', None)
        return round(avg_score) if avg_score is not None else None


class TitleCRUDSerializer(serializers.ModelSerializer):

    """Сериализатор для создания, обновления, обработки данных"""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        fields = ('__all__')
        model = Title

    def validate_genre(self, value):
        """Валидация жанров"""
        if not value or len(value) == 0:
            raise serializers.ValidationError('Жанры не могут быть пустыми')
        return value

    def to_representation(self, instance):
        """Сериализует объект через TitleSerializer."""
        return TitleSerializer(instance, context=self.context).data


class ReviewsSerializer(serializers.ModelSerializer):

    """Сериализатор для отзывов на произведения."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date',)
        read_only_fields = ('author', 'pub_date', 'title')

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')

        if request.method == 'POST':
            if Review.objects.filter(
                author=request.user, title_id=title_id
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение.'
                )
        return data

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError('Оценка должна быть от 1 до 10.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам на произведения."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta():
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author', 'reviews')
