from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year_not_future(value):
    """Проверяет, что переданный год не больше текущего.

    Args:
        value: Год для проверки.

    Raises:
        ValidationError: Если переданный год больше текущего.

    Returns:
        None: Функция ничего не возвращает в случае успеха.
    """

    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год {value} не должен быть больше текущего ({current_year})'
        )
