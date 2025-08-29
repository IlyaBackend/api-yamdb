from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from api_yamdb.constants import MY_USER_PROFILE, REGULAR_USERNAME


def validate_username(value):
    if value == MY_USER_PROFILE:
        raise ValidationError(
            f'Нельзя использовать {MY_USER_PROFILE} в качестве username'
        )


username_validator = RegexValidator(
    regex=REGULAR_USERNAME,
    message=(
        'Имя пользователя может содержать буквы, цифры, и некоторые знаки'
    )
)
