from django.db.models import Count, Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleSerializer, TitleCRUDSerializer
)
from titles.models import Category, Genre, Review, Title


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

# class TitleViewSet(viewsets.ModelViewSet):
#     """Класс для управления отзывов на произведения."""
#     serializer_class = TitleSerializer

#     def get_title_info(self):
#         return Title.objects.annotate(
#             average_rating=Avg('reviews__rating'),
#             reviews_number=Count('reviews'),
#         ).order_by('-average_rating')


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс для управления отзывов на произведения."""
    serializer_class = ReviewSerializer
    lookup_field = 'id'
    permission_classes = [IsAdmin, IsAuthenticatedOrReadOnly]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Класс для управления комментариев к отзывам."""
    serializer_class = CommentSerializer
    lookup_field = 'id'
    permission_classes = [IsAdmin, IsAuthenticatedOrReadOnly]

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
