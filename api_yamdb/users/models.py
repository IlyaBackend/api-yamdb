from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.db import models

from api_yamdb.constants import (EMAIL_MAX_LENGTH, MY_USER_PROFILE,
                                 ROLE_CHOICES, ROLE_MAX_LENGTH, ROLE_USER)


class Account(AbstractUser):

    """
    Кастомная моедль пользователя
    """
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Email'
    )
    role = models.CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        verbose_name='Роль'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )

    def save(self, *args, **kwargs):
        self.clean()
        if self.is_staff and self.role != 'moderator':
            self.role = 'admin'
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id', 'username',)

    def generate_confirmation_code(self):
        """
        Генерирует и возвращает токен подтверждения для пользователя.
        """
        return default_token_generator.make_token(self)

    def check_confirmation_code(self, token):
        """
        Проверяет, является ли переданный токен действительным.
        """
        return default_token_generator.check_token(self, token)

    def clean(self):
        super().clean()
        if self.username == MY_USER_PROFILE:
            raise ValidationError({
                'username': 'Нельзя использовать "me" в качестве username'
            })

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def is_admin(self):
        return self.role == 'admin' or self.is_staff
