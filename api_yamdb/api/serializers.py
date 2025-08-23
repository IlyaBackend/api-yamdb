from django.contrib.auth import get_user_model
from rest_framework import serializers

from titles.models import Category, Genre, Title

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        fields = '__all__'
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        fields = '__all__'
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""
    # Добавил две строчки в код Алексея, связанных данных,
    # для лучшего вывода API.
    category = CategorySerializer(read_only=True)  # Добавил
    genre = GenreSerializer(many=True, read_only=True)  # Добавил
    average_rating = serializers.SerializerMethodField(read_only=True)
    reviews_number = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'description', 'category', 'genre',
            'average_rating', 'reviews_rating'
        ]

    def get_average_rating(self, title):
        """
        Возвращает среднюю оценку произведения
        или сообщение об отсутствии отзывов.
        """
        avg_rating = getattr(title, 'average_rating', None)
        return round(avg_rating) if avg_rating is not None else (
            f'Произведение {title.name} еще не имеет отзывов.')


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
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title
