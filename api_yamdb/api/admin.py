from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import Account


@admin.register(Account)
class AccountAdmin(UserAdmin):
    model = Account
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Персональная информация', {'fields': (
            'first_name', 'last_name', 'bio')}),
        ('Права доступа', {'fields': (
            'role', 'is_staff', 'is_active', 'is_superuser'
        )}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name', 'slug')
    list_editable = ('name', 'slug')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name', 'slug')
    list_editable = ('name', 'slug')


@admin.register(Title)
class TitlesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'get_genres_list', 'category')
    search_fields = ('name', 'category__name')

    @admin.display(description=_('Жанры'))
    def get_genres_list(self, title):
        return ', '.join(genre.name for genre in title.genres.all())


@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'text', 'author', 'score', 'pub_date')
    search_fields = ('text',)
    list_editable = ('text', 'author', 'score')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'reviews', 'author', 'text', 'pub_date')
    search_fields = ('text',)
    list_editable = ('text', 'author')
