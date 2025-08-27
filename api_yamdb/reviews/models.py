from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


from api_yamdb.constants import (
    CATEGORY_GENRE_MAX_LENGTH, RATING_MAX_VALUE, RATING_MIN_VALUE, STR_LENGTH
)
from .validators import validate_year_not_future


User = get_user_model()


class CategoryGenreBase(models.Model):
    """Абстрактная модель для категорий и жанров."""

    name = models.CharField(
        max_length=CATEGORY_GENRE_MAX_LENGTH,

        verbose_name='Название'
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(CategoryGenreBase):
    """Модель категорий."""

    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreBase):
    """Модель жанров."""

    class Meta(CategoryGenreBase.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):

    """ Модель произведений."""


    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения'
    )

    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=[validate_year_not_future],
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
        return (self.name[:STR_LENGTH])


class TitleGenre(models.Model):

    """ Модель связывающая произведения и жанры."""


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


class AuthorContentModel(models.Model):
    """Абстрактная базовая модель с текстом, автором и датой публикации."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:STR_LENGTH]


class Review(AuthorContentModel):
    """Модель отзыва на произведение."""

    title = models.ForeignKey(

        Title,

        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(RATING_MIN_VALUE),
            MaxValueValidator(RATING_MAX_VALUE)
        ],
        verbose_name='Оценка произведения'
    )

    class Meta(AuthorContentModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'

    def __str__(self):
        return (
            f'Отзыв {self.author.username} на {self.title}. '
            f'Оценка: {self.score}.'
        )


class Comment(AuthorContentModel):
    """Модель комментария к отзыву на произведение."""

    reviews = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Обзор'
    )

    class Meta(AuthorContentModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
