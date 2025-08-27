from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from .constants import RATING_MIN_VALUE, RATING_MAX_VALUE


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
    rating = serializers.PositiveIntegerField(read_only=True)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        ]


class TitleCRUDSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, обновления, обработки данных"""

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

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date',)

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
