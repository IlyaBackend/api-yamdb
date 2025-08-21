from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path(
        'v1/auth/signup/',
        UserViewSet.as_view({'post': 'signup'}), name='signup'
    ),
    path(
        'v1/auth/token/',
        UserViewSet.as_view({'post': 'token'}), name='token'
    ),
    path(
        'v1/users/me/',
        UserViewSet.as_view({'get': 'me', 'patch': 'me'}), name='me'
    ),
    path('v1/', include(router.urls)),
    # path('v1/', include('djoser.urls.jwt'))
]
