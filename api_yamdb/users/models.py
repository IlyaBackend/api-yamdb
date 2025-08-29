from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.db import models

from api_yamdb.constants import (EMAIL_MAX_LENGTH, MY_USER_PROFILE, ROLE_ADMIN,
                                 ROLE_CHOICES, ROLE_MAX_LENGTH, ROLE_MODERATOR,
                                 ROLE_USER, USERNAME_MAX_LENGTH)
from users.validators import username_validator, validate_username


class Account(AbstractUser):
    """Кастомная моедль пользователя."""

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[validate_username, username_validator],
        verbose_name='Имя пользователя'
    )
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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id', 'username',)

    def save(self, *args, **kwargs):
        self.clean()
        if self.is_staff and self.role != ROLE_MODERATOR:
            self.role = ROLE_ADMIN
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.username == MY_USER_PROFILE:
            raise ValidationError({
                'username':
                f'Нельзя использовать {MY_USER_PROFILE} в качестве username'
            })

    def generate_confirmation_code(self):
        """Генерирует одноразовый код подтверждения для пользователя."""
        return default_token_generator.make_token(self)

    def check_confirmation_code(self, token):
        """Проверяет, является ли переданный токен действительным."""
        return default_token_generator.check_token(self, token)

    @property
    def is_moderator(self):
        return self.role == ROLE_MODERATOR

    def is_admin(self):
        return self.role == ROLE_ADMIN or self.is_staff
