"""Votes viewsets"""
from rest_framework import status, viewsets
from .models import Vote
from .serializers import VoteSerializer

from .permissions import IsVoteOwnerOrReadOnly


class VoteViewSet(viewsets.ModelViewSet):
    """
    Votes viewset
    """
    queryset = Vote.objects
    serializer_class = VoteSerializer
    permission_classes = (IsVoteOwnerOrReadOnly, )
