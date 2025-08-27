import csv
import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from reviews.models import Category, Genre, Title, Review, Comment, TitleGenre
from api_yamdb.settings import BASE_DIR

User = get_user_model()

# проверить работоспособность командой |python manage.py import_csv|


class Command(BaseCommand):
    """Команда для импорта данных из CSV файлов."""

    def handle(self, *args, **options):
        models_files = [
            (Category, 'category.csv'),
            (Genre, 'genre.csv'),
            (User, 'users.csv'),
            (Title, 'titles.csv'),
            (TitleGenre, 'genre_title.csv'),
            (Review, 'review.csv'),
            (Comment, 'comments.csv'),
        ]

        for model, filename in models_files:
            self.import_model(model, filename)

    def import_model(self, model, filename):
        """Импортирует данные для одной модели."""

        filepath = os.path.join(BASE_DIR, 'static', 'data', filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.process_row(row, model)
                    model.objects.update_or_create(id=row['id'], defaults=row)

            self.stdout.write(
                self.style.SUCCESS(f'Успешно импортировано: {filename}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка в {filename}: {e}'))

    def process_row(self, row, model):
        field_mappings = {
            Title: {'category': 'category_id'},
            Review: {'author': 'author_id', 'title': 'title_id'},
            Comment: {'author': 'author_id', 'review': 'review_id'},
        }

        mapping = field_mappings.get(model, {})
        for old_field, new_field in mapping.items():
            if old_field in row:
                row[new_field] = row.pop(old_field)

        numeric_fields = [
            'id',
            'category_id',
            'author_id',
            'title_id',
            'review_id',
            'pub_year',
            'score'
        ]

        for key, value in row.items():
            if key in numeric_fields and value and value.isdigit():
                row[key] = int(value)
