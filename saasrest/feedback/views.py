from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from .models import Feedback
from .permissions import IsOwnerOrReadOnly
from .serializers import FeedbackSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    Feedback from users viewset
    """
    queryset = Feedback.objects.order_by('-created_at')
    serializer_class = FeedbackSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )

    # read only
    def get_queryset(self):
        if self.request.user:
            return self.queryset.filter(author=self.request.user)
        else:
            raise PermissionDenied()

    def perform_create(self, serializer):
        if self.request.user:
            serializer.save(author=self.request.user)
        else:
            raise PermissionDenied()
