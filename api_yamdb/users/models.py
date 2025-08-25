import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models


ROLE_CHOICES = [
    ('user', 'Аутентифицированный пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
    ('superuser', 'Суперпользователь'),
]


class CustomUser(AbstractUser):
    """
    Кастомная моедль пользователя
    """
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль'
    )
    bio = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Биография'
    )
    confirmation_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None,
        verbose_name='Код подтверждения'
    )

    class meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id', 'username',)
        default_related_name = 'users'

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'superuser'
        elif self.is_staff and self.role != 'superuser':
            self.role = 'admin'
        super().save(*args, **kwargs)

    def generate_confirmation_code(self):
        self.confirmation_code = secrets.token_urlsafe(20)
        self.save()

    def is_moderator(self):
        return self.role == 'moderator' or self.is_staff

    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
