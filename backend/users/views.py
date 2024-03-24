from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import UserFollow
from .serializers import CustomUserSerializer, UserFollowSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        if self.action == 'subscriptions':
            user = self.request.user
            return UserFollow.objects.filter(user_from=user).select_related('user_to').order_by('-created')
        return super().get_queryset()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserFollowSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = UserFollowSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='subscribe')
    def subscribe(self, request, pk=None):
        return self._manage_subscription(request, pk, True)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='unsubscribe')
    def unsubscribe(self, request, pk=None):
        return self._manage_subscription(request, pk, False)

    def _manage_subscription(self, request, pk, is_subscribe):
        user_to = get_object_or_404(User, pk=pk)
        if user_to == request.user:
            return Response({"detail": "You cannot subscribe to yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if is_subscribe:
            _, created = UserFollow.objects.get_or_create(user_from=request.user, user_to=user_to)
            if created:
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "Already subscribed."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            subscription = UserFollow.objects.filter(user_from=request.user, user_to=user_to)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"detail": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND)


