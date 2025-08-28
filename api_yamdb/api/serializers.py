from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api_yamdb.constants import (CONFIRMATION_CODE_MAX_LENGTH,
                                 EMAIL_MAX_LENGTH, RATING_MAX_VALUE,
                                 RATING_MIN_VALUE, REGULAR_USERNAME, ROLE_USER,
                                 USERNAME_MAX_LENGTH)
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Принимает только username и email.
    """

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

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        return user

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        User(**attrs).clean()
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


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для администратора.

    Админ умеет создавать пользователей и назначать им роль.
    """

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для валидации username, confirmation_code

    и последующего создания токена.
    """

    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_MAX_LENGTH, required=True
    )

    def validate(self, data):
        user = get_object_or_404(User, username=data.get('username'))
        if not user.check_confirmation_code(data.get('confirmation_code')):
            raise ValidationError(
                {'error': 'Код подтверждения неверен.'}
            )
        self.context[ROLE_USER] = user
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
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        ]


class TitleCRUDSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, обновления, обработки данных."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=True,
        allow_empty=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=True
    )

    class Meta:
        fields = '__all__'
        model = Title

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
    score = serializers.IntegerField(
        min_value=RATING_MIN_VALUE, max_value=RATING_MAX_VALUE
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date')

    def validate(self, data):
        request = self.context['request']

        if request.method == 'POST':
            if Review.objects.filter(
                author=request.user,
                title_id=self.context['view'].kwargs.get('title_id')
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение.'
                )
        return data

    def validate_score(self, value):
        if not RATING_MIN_VALUE <= value <= RATING_MAX_VALUE:
            raise serializers.ValidationError(
                f'Оценка должна быть от {self.RATING_MIN_VALUE} '
                f'до {self.RATING_MAX_VALUE}.'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам на произведения."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta():
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
