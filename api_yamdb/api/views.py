from django.db.models import Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filters import TitleFilters
from .permissions import IsAdminOrReadOnly, IsAuthorAdminModeratorOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewsSerializer,
    TitleSerializer,
    TitleCRUDSerializer
)
from reviews.models import Category, Genre, Review, Title


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Базовый вьюсет для категорий и жанров
    """
    pagination_class = StandardPagination
    filter_backends = (filters.SearchFilter,)


class CategoryViewSet(CreateListDestroyViewSet):
    """Класс для управления категориями"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """Класс для управления жанрами"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Класс для управления произведениями"""
    queryset = Title.objects.annotate(
        score=Avg('reviews__score'),
        reviews_number=Count('reviews')
    ).all().order_by('-year', 'name',)
    pagination_class = StandardPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name', 'description')
    filterset_class = TitleFilters
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        return (
            TitleCRUDSerializer
            if self.action in ('create', 'partial_update', 'update')
            else TitleSerializer
        )


class ReviewsViewSet(viewsets.ModelViewSet):
    """Класс для управления отзывов на произведения."""
    serializer_class = ReviewsSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAuthorAdminModeratorOrReadOnly
    )
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all().order_by('pub_date',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Класс для управления комментариев к отзывам."""
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAuthorAdminModeratorOrReadOnly
    )
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs['review_id'],
            title__id=self.kwargs['title_id']
        )

    def get_queryset(self):
        return self.get_review().comments.all().order_by('pub_date',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, reviews=self.get_review())
