from django.urls import path, include
from rest_framework.routers import DefaultRouter
from djoser.urls.authtoken import urlpatterns as auth_urlpatterns

from .views import CustomUserViewSet


router = DefaultRouter()
router.register(r'users', CustomUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_urlpatterns)),
]
