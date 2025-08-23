from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleCRUDSerializer
)
from titles.models import Category, Genre, Title


class CategoryViewSet(viewsets.ModelViewSet):
    """Класс для управления категориями"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(viewsets.ModelViewSet):
    """Класс для управления жанрами"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Класс для управления произведениями"""
    queryset = Title.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'description')
    filterset_fields = ('year', 'category', 'genre')

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update', 'update'):
            return TitleCRUDSerializer
        return TitleSerializer
