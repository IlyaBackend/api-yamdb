from rest_framework import serializers
from reviews.models import Category, Comment, Review, Genre, Title


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
    # rating_number = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
            # 'rating_number'
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
            raise serializers.ValidationError("Жанры не могут быть пустыми")
        return value

    def to_representation(self, instance):
        """Сериализует объект через TitleSerializer."""
        serializer = TitleSerializer(instance, context=self.context)
        return serializer.data


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
        user = request.user

        if request.method == 'POST':
            if Review.objects.filter(author=user, title_id=title_id).exists():
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
        fields = ('id', 'text', 'author', 'pub_date', 'reviews')
        read_only_fields = ('author', 'reviews')
