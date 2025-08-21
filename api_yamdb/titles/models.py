from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models

# Константа, ограничиваем в 20 символов.
STR_LENGTH = 20


class Category(models.Model):
    """ Модель категорий. """
    name = models.CharField(max_length=256, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="Слаг категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return f'{self.name}'


class Genre(models.Model):
    """ Модель Жанры """
    name = models.CharField(max_length=256, verbose_name="Название жанра")
    slug = models.SlugField(unique=True, verbose_name="Слаг жанра")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    """ Модель произведений """
    name = models.CharField(
        max_length=256,
        verbose_name="Название произведения"
    )

    # Год выпуска должен быть положительным.
    year = models.PositiveIntegerField(
        verbose_name="Год выпуска",

        # Валидатор обернул в кортеж, но не уверен,
        # может лучше список, на случай добавлений/изменений?
        validators=(
            MaxValueValidator(
                datetime.now().year,
                message="Год не должен быть больше текущего")
        ),
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles",
        verbose_name="Категория"
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        related_name='titles',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    # На случай если название произведения
    # будет длинным, лучше ограничить 20 символами.

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
        verbose_name = "Жанр-Произведение"
        verbose_name_plural = "Жанры-произведения"
        # constraints для избежания дубликатов,
        # тоже сделал кортеж, здесь ничего менять и
        # добавляться не должно, так что думаю что это верно.
        constraints = (
            models.UniqueConstraint(
                fields=["title", "genre"],
                name="unique_id_title_genre"
            )
        )

    def __str__(self):
        return f"{self.title}-{self.genre}"
