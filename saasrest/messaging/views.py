from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from asgiref.sync import async_to_sync
from saas_core.utils import (broadcast_deleted_message, broadcast_message,
                             notify_user)

from .models import Conversation, Message, MessageImage
from .permissions import IsOwner
from .serializers import (ConversationSerializer, MessageImageSerializer,
                          MessageSerializer)


class MessageImageViewSet(viewsets.ModelViewSet):
    """
    MessageImage viewset
    """
    queryset = MessageImage.objects
    serializer_class = MessageImageSerializer
    permission_classes = (IsAuthenticated, IsOwner, )

    def get_queryset(self):
        if self.request.user:
            return self.queryset.filter(conversation__users__in=[self.request.user])
        else:
            raise PermissionDenied()


class MessageViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Message.objects
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated, IsOwner, )
    filter_backends = (filters.SearchFilter,
                       DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ('created_at', )
    search_fields = ('text')
    filter_fields = ('conversation__id',)

    def perform_create(self, serializer):
        if self.request.user:
            msg = serializer.save(author=self.request.user)
            # serializer_1 = self.serializer_class(msg, many=False, )
            async_to_sync(broadcast_message)(msg, serializer.data)
        else:
            raise PermissionDenied()

    def perform_destroy(self, instance):
        conversation_id = instance.conversation.id
        msg_id = instance.id
        instance.delete()
        async_to_sync(broadcast_deleted_message)(conversation_id, msg_id)

    def get_queryset(self):
        if self.request.user:
            return self.queryset.filter(conversation__users__in=[self.request.user])
        else:
            raise PermissionDenied()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    Conversation viewset
    """
    queryset = Conversation.objects
    serializer_class = ConversationSerializer
    permission_classes = (IsAuthenticated, IsOwner, )
    filter_backends = (filters.SearchFilter,
                       DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ('created_at', 'updated_at')
    search_fields = ('title', 'users__first_name', 'users__last_name')

    def get_queryset(self):
        if self.request.user:
            return self.queryset.filter(users__in=[self.request.user])
        else:
            raise PermissionDenied()

    @action(detail=False, methods=['get'], url_path=r'get_by_user_id/(?P<uid>\d+)')
    def get_by_users_ids(self, request, uid):
        """get conversation by users ids (uid and request user uid)"""
        if request.user.id == int(uid):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        q = self.queryset.filter(users=request.user.id).filter(users=uid)
        if q.exists():
            serializer = ConversationSerializer(
                q.first(), many=False, context={'request': request})
            return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)
