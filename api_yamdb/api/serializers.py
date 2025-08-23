from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from titles.models import Comment, Review, Title

# User = get_user_model()


# class TitleSerializer(serializers.ModelSerializer):
#     """Сериализатор для произведений."""
#     average_rating = serializers.SerializerMethodField(read_only=True)
#     reviews_number = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = Title
#         fields = [
#             'id', 'name', 'year', 'description', 'category', 'genre',
#             'average_rating', 'reviews_rating'
#         ]

#     def get_average_rating(self, title):
#         """
#         Возвращает среднюю оценку произведения
#         или сообщение об отсутствии отзывов.
#         """
#         avg_rating = getattr(title, 'average_rating', None)
#         return round(avg_rating) if avg_rating is not None else (
#             f'Произведение {title.name} еще не имеет отзывов.')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов на произведения."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    title = serializers.SlugRelatedField(
        slug_field='name', queryset=Title.objects.all()
    )

    class Meta:
        model = Review
        fields = '__all__'
        validators = [UniqueTogetherValidator(
            queryset=Review.objects.all(),
            fields=('author', 'title'),
        )]

    def validate_title(self, title):
        """Валидатор для проверки уникальности отзыва на произведение."""
        if Review.objects.filter(
            author=self.context['request'].user, title=title
        ).exists():
            raise serializers.ValidationError(
                'Отзыв на это произведение уже создан.')
        return title


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам на произведения."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta():
        model = Comment
        fields = '__all__'
        read_only_fields = ('review',)
