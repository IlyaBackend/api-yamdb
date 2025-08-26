from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year_not_future(value):
    """
    Валидатор для проверки, что год не больше текущего.
    Вызывается при каждой проверке поля.
    """
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год {value} не должен быть больше текущего ({current_year})'
        )
