from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .models import CustomUser
from .permissions import IsAdmin
from .serializers import (
    UserSignUpSerializer,
    UserSerializer,
    AdminUserSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    Класс полностью отвечает за управление пользователями и аутентификацикей
    """
    queryset = CustomUser.objects.all().order_by('id', 'username')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        """
        Разные права доступа для разных действий
        """
        return [IsAuthenticated()] if self.action == 'me' else (
            super().get_permissions())

    def get_serializer_class(self):
        return UserSerializer if self.action == 'me' else AdminUserSerializer

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        """
        Просмотр и редактирование своего профиля
        """
        user = request.user
        if request.method == 'GET':
            return Response(UserSerializer(user).data)
        serializer = UserSerializer(
            user, data=request.data, partial=True
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
    user, _ = CustomUser.objects.get_or_create(
        **serializer.validated_data
    )
    user.generate_confirmation_code()
    send_mail(
        subject='Yamdb confirmation code',
        message=f'Ваш код подтверждения: {user.confirmation_code}',
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
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')
    if not username or not confirmation_code:
        return Response(
            {'error': 'Поля "username" и "confirmation_code" обязательны.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'Пользователь не найден.'},
            status=status.HTTP_404_NOT_FOUND
        )
    if user.confirmation_code != confirmation_code:
        return Response(
            {'error': 'Отсутствует обязательное поле или оно некорректно'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {'token': str(AccessToken.for_user(user))}, status=status.HTTP_200_OK)
