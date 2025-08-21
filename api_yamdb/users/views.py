from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .models import CustomUser
from .serializers import (
    UserSignUpSerializer,
    UserSerializer,
    AdminUserSerializer
)
from .permissions import IsAdmin


class UserViewSet(viewsets.ModelViewSet):
    '''
    Класс полностью отвечает за управление пользователями и аутентификацикей
    '''
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'

    def get_permissions(self):
        '''
        Разные права доступа для разных действий
        '''
        if self.action in ['signup', 'token']:
            return [AllowAny()]
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['me']:
            return UserSerializer
        if self.action in ['signup']:
            return UserSerializer
        return AdminUserSerializer

    @action(
        methods=['post'],
        detail=False,
        permission_classes=[AllowAny()],
        url_path='auth/signup'
    )
    def signup(self, request):
        '''
        регистрация пользователя и кода
        '''
        if request.data.get('username') == 'me':
            return Response(
                {'username': ['Такой username занят']},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = CustomUser.objects.get_or_create(
            **serializer.validated_data
        )
        if not created:
            # Пользователь уже существует, возвращаем ошибку
            return Response(
                {'error': 'Пользователь с подобными данными уже существует'},
                status=status.HTTP_400_BAD_REQUEST)
        # try:
        #     user = CustomUser.objects.get(
        #         username=serializer.validated_data.get('username'),
        #         email=serializer.validated_data.get('email')
        #     )
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        # except CustomUser.DoesNotExist:
        #     user = CustomUser.objects.create(
        #         **serializer.validated_data
        #     )
        user.generate_confirmation_code()
        send_mail(
            subject='Yamdb confirmation code',
            message=f'Ваш код подтверждения: {user.confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        permission_classes=[AllowAny()],
        url_path='auth/token/'
    )
    def token(self, request):
        '''
        Выдача токена по username и коду
        '''
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')
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
        token = AccessToken.for_user(user)
        return Response({'token': str(token)})

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[IsAuthenticated()],
        url_path='users/me'
    )
    def me(self, request):
        '''
        Просмотр и редактирование своего профиля
        '''
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        serializer = UserSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
