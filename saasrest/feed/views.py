from django.shortcuts import render

# Create your views here.

"""FeedPosts views"""
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from django_filters import rest_framework as django_rest_filters
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tags.models import Tag
from votes.models import Vote
from votes.serializers import VoteSerializer

from .models import FeedPost

from .permissions import IsOwnerOrReadOnly
from saas_core.permissions import IsAuthenticatedAndVerified
from .serializers import FeedPostSerializer

import random

from django.utils.translation import ugettext as _


class FeedPostFilter(django_rest_filters.FilterSet):
    """Custom filter for feed_posts"""
    class Meta:
        model = FeedPost
        fields = ['tags', 'author_id' ]

    # tricky part - how to filter by related field?
    # but not by its foreign key (default)
    # `to_field_name` is crucial here
    # `conjoined=True` makes that, the more tags, the more narrow the search
    tags = django_rest_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects,
        to_field_name='name',
        conjoined=True,
        method='filter_tags'
    )

    def filter_tags(self, queryset, name, tags):
        if tags:
            q = queryset.distinct().filter(tags__in=tags)
            return q
        else:
            return queryset


class FeedPostViewSet(viewsets.ModelViewSet):
    """
    FeedPosts Viewset
    """
    queryset = FeedPost.objects\
        .prefetch_related('tags').prefetch_related('images')\
        .order_by('-created_at')
    serializer_class = FeedPostSerializer

    permission_classes = (IsOwnerOrReadOnly, )

    filter_backends = (filters.SearchFilter,
                       django_rest_filters.DjangoFilterBackend,
                       filters.OrderingFilter)
    ordering_fields = ('price', 'created_at', 'score')
    search_fields = ('text',)
    # filter_fields = ('author', 'author_id', 'tags__contain')
    filter_class = FeedPostFilter

    def perform_create(self, serializer):
        if self.request.user:
            serializer.save(author=self.request.user)
        else:
            raise PermissionDenied()

    # read only
    @action(detail=False, methods=['get'])
    def my(self, request):
        if self.request.user:
            queryset = self.queryset.filter(author=self.request.user)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = FeedPostSerializer(
                    page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)

            serializer = FeedPostSerializer(
                queryset, many=True, context={'request': request})
            return Response(serializer.data)
        else:
            raise PermissionDenied()

    def vote(self, request, pk, votetype):
        if self.request.user:
            current_feed_post = self.get_object()
            if current_feed_post.votes.filter(user=self.request.user).exists():
                return Response({'detail': _("Already voted.")}, status=status.HTTP_400_BAD_REQUEST)
            vote = current_feed_post.votes.create(
                activity_type=votetype, user=request.user)
            serializer = VoteSerializer(
                vote, many=False, context={'request': request})
            return Response(serializer.data)
        else:
            raise PermissionDenied()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedAndVerified, ])
    def upvote(self, request, pk=None):
        return self.vote(request, pk, Vote.UP_VOTE)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedAndVerified, ])
    def downvote(self, request, pk=None):
        return self.vote(request, pk, Vote.DOWN_VOTE)

