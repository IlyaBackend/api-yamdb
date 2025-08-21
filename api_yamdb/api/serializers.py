from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from titles.models import Comment, Review, Title

User = get_user_model()


class TitleSerializer(serializers.ModelSerializer):
    pass


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
