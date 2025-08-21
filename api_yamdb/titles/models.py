from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()

STR_LENGTH = 20


class Title(models.Model):
    pass


class Review(models.Model):
    """Модель отзыва на произведение."""
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='Произведение'
    )
    text = models.TextField(null=True, blank=True, verbose_name='Отзыв')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка произведения'
    )
    created_at = models.DateTimeField(
        'Дата добавления отзыва', auto_now_add=True
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['author', 'title'], name='unique_review'),]
        ordering = ('created_at',)
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'

    def __str__(self):
        return (
            f'Отзыв {self.author.username} на {self.title}.'
            f'{self.text}. Оценка: {self.rating}.'
        )


class Comment(models.Model):
    """Модель комментария к отзыву на произведение."""
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    text = models.TextField(
        null=False, blank=False, verbose_name='Комментарий'
    )
    created_at = models.DateTimeField(
        'Дата добавления комментария', auto_now_add=True
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:STR_LENGTH]
