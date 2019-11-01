from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .permissions import IsOwnerOrReadOnly
from .serializers import NotificationSerializer

from saas_core.config import DEFAULT_PERMISSION_CLASSES

class NotificationViewSet(viewsets.ModelViewSet):
    """
    Notifications viewset
    """
    queryset = Notification.objects.order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = DEFAULT_PERMISSION_CLASSES + [IsAuthenticated, IsOwnerOrReadOnly, ]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('recipient__first_name',
                     'recipient__last_name', 'title', 'text')
    # filter_fields = ('recipient__id')

    # read only
    def get_queryset(self):
        return self.queryset.filter(recipient=self.request.user)
