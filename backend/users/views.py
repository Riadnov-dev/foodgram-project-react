from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UserFollow
from .permissions import IsAuthenticatedAndOwner
from .serializers import CustomUserSerializer, UserSubscriptionSerializer


User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticatedAndOwner]
        elif self.action in ['create', 'list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action == 'subscriptions':
            user = self.request.user
            return (UserFollow.objects.filter(user_from=user)
                    .select_related('user_to').order_by('-created')
                    )
        elif self.action == 'list':
            return User.objects.all()
        else:
            return super().get_queryset()

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='subscriptions')
    def subscriptions(self, request):
        user_ids = (UserFollow.objects.filter(user_from=request.user)
                    .values_list('user_to', flat=True))
        users = User.objects.filter(id__in=user_ids)

        recipes_limit = request.query_params.get('recipes_limit')
        try:
            recipes_limit = (int(recipes_limit) if recipes_limit
                             is not None else None)
        except ValueError:
            recipes_limit = None

        page = self.paginate_queryset(users)
        if page is not None:
            serializer = UserSubscriptionSerializer(
                page,
                many=True,
                context={
                    'request': request,
                    'recipes_limit': recipes_limit})
            return self.get_paginated_response(serializer.data)

        serializer = UserSubscriptionSerializer(
            users,
            many=True,
            context={'request': request,
                     'recipes_limit': recipes_limit})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated], url_path='subscribe')
    def manage_subscription(self, request, id=None):
        user_to = get_object_or_404(User, pk=id)

        if user_to == request.user:
            return Response(
                {"detail": "You cannot subscribe or unsubscribe to yourself."},
                status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            _, created = UserFollow.objects.get_or_create(
                user_from=request.user,
                user_to=user_to)
            if created:
                recipes_limit = request.query_params.get('recipes_limit')
                context = {'request': request}
                if recipes_limit:
                    try:
                        context['recipes_limit'] = int(recipes_limit)
                    except ValueError:
                        pass
                return Response(UserSubscriptionSerializer(
                    user_to,
                    context=context).data,
                    status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"detail": "Already subscribed."},
                    status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            subscription = UserFollow.objects.filter(
                user_from=request.user,
                user_to=user_to)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"detail": "Subscription not found."},
                    status=status.HTTP_400_BAD_REQUEST)
