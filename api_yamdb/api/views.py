from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.constants import MY_USER_PROFILE
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilters
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorAdminModeratorOrReadOnly)
from .serializers import (AdminUserSerializer, CategorySerializer,
                          CommentSerializer, GenreSerializer,
                          ReviewsSerializer, TitleCRUDSerializer,
                          TitleSerializer, TokenSerializer,
                          UserSignUpSerializer)


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


class UserViewSet(viewsets.ModelViewSet):

    """
    Класс полностью отвечает за управление пользователями и аутентификацикей
    """
    queryset = User.objects.all().order_by('id', 'username')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path=MY_USER_PROFILE
    )
    def me(self, request):
        """
        Просмотр и редактирование своего профиля
        """
        user = request.user
        if request.method == 'GET':
            return Response(AdminUserSerializer(user).data)
        serializer = AdminUserSerializer(
            user, data=request.data, partial=True,
            context={'request': request, 'view': self}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    регистрация пользователя и кода
    """
    serializer = UserSignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    confirmation_code = user.generate_confirmation_code()
    send_mail(
        subject='Yamdb confirmation code',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """
    Выдача токена по username и коду
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(
        {'token': str(AccessToken.for_user(serializer.context.get('user')))},
        status=status.HTTP_200_OK
    )


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
        score=Avg('reviews__score')).all().order_by('-year', 'name',)
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
