from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import CustomUser

User = CustomUser

STR_LENGTH = 20


class Category(models.Model):
    """ Модель категорий. """
    name = models.CharField(max_length=256, verbose_name='Название категории')
    slug = models.SlugField(unique=True, verbose_name='Слаг категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Genre(models.Model):
    """ Модель Жанры """
    name = models.CharField(max_length=256, verbose_name='Название жанра')
    slug = models.SlugField(unique=True, verbose_name='Слаг жанра')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """ Модель произведений """
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения'
    )

    year = models.PositiveIntegerField(
        verbose_name='Год выпуска',
        validators=[
            MaxValueValidator(
                datetime.now().year,
                message='Год не должен быть больше текущего')
        ],
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name',)
        default_related_name = 'titles'

    def __str__(self):
        return (self.name[:STR_LENGTH] + '...'
                if len(self.name) > STR_LENGTH else self.name)


class TitleGenre(models.Model):
    """ Модель связывающая произведения и жанры """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Жанр-Произведение'
        verbose_name_plural = 'Жанры-произведения'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_id_title_genre'
            )
        ]

    def __str__(self):
        return f'{self.title}-{self.genre}'


class Review(models.Model):
    """Модель отзыва на произведение."""
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Отзыв')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка произведения'
    )
    pub_date = models.DateTimeField(
        'Дата добавления отзыва', auto_now_add=True
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['author', 'title'], name='unique_review'),]
        ordering = ('pub_date',)
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'

    def __str__(self):
        return (
            f'Отзыв {self.author.username} на {self.title}.'
            f'{self.text}. Оценка: {self.score}.'
        )


class Comment(models.Model):
    """Модель комментария к отзыву на произведение."""
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    reviews = models.ForeignKey(Review, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Комментарий')
    pub_date = models.DateTimeField(
        'Дата добавления комментария', auto_now_add=True
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return self.text[:STR_LENGTH]
