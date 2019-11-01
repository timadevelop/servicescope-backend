"""Votes viewsets"""
from rest_framework import status, viewsets
from .models import Vote
from .serializers import VoteSerializer

from .permissions import IsVoteOwnerOrReadOnly

from saas_core.config import DEFAULT_PERMISSION_CLASSES

class VoteViewSet(viewsets.ModelViewSet):
    """
    Votes viewset
    """
    queryset = Vote.objects
    serializer_class = VoteSerializer
    permission_classes = DEFAULT_PERMISSION_CLASSES + [IsVoteOwnerOrReadOnly, ]
