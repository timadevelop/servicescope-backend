"""Services views"""
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from django_filters import rest_framework as django_rest_filters
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from categories.models import Category
from tags.models import Tag
from votes.models import Vote
from votes.serializers import VoteSerializer

from .models import Service, ServicePromotion
from .permissions import IsOwnerOrReadOnly
from saas_core.permissions import IsAuthenticatedAndVerified
from .serializers import (ServicePromotionSerializer,
                          ServiceSerializer)

import random

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from django.utils.translation import ugettext as _


class ServiceFilter(django_rest_filters.FilterSet):
    """Custom filter for services"""
    class Meta:
        model = Service
        fields = ['tags', 'category',
                  'location_id', 'price', 'author_id']

    price = django_rest_filters.RangeFilter()
    # default for CharFilter is to have exact lookup_type
    # title = django_rest_filters.CharFilter()
    # description = django_rest_filters.CharFilter()

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

    category = django_rest_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects,
        to_field_name='name',
        conjoined=True,
        method='filter_category'
    )

    def filter_tags(self, queryset, name, tags):
        if tags:
            q = queryset.filter(tags__in=tags).distinct()
            return q
        else:
            return queryset

    def filter_category(self, queryset, name, categories):
        if categories and len(categories) > 0:
            return queryset.filter(category=categories[0])
        else:
            return queryset


class ServiceViewSet(viewsets.ModelViewSet):
    """
    Services Viewset
    """
    queryset = Service.objects\
        .prefetch_related('tags').prefetch_related('images')\
        .select_related('category').select_related('location')\
        .order_by('-created_at')
    serializer_class = ServiceSerializer

    permission_classes = (IsOwnerOrReadOnly, )

    filter_backends = (filters.SearchFilter,
                       django_rest_filters.DjangoFilterBackend,
                       filters.OrderingFilter)
    ordering_fields = ('price', 'created_at', 'score')
    search_fields = ('title', 'description',)
    filter_class = ServiceFilter

    # one minute cache
    # @method_decorator(cache_page(60*1))
    # @method_decorator(vary_on_cookie)
    # def dispatch(self, *args, **kwargs):
    #     return super(self.__class__, self).dispatch(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Custom list processing, exclude promoted services
        (use service-promotion view instead)
        """
        self.queryset = self.get_queryset().filter(
            Q(promoted_til__lt=timezone.now()) | Q(promoted_til=None))
        return super().list(request, *args, **kwargs)

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
                serializer = ServiceSerializer(
                    page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)

            serializer = ServiceSerializer(
                queryset, many=True, context={'request': request})
            return Response(serializer.data)
        else:
            raise PermissionDenied()

    def vote(self, request, pk, votetype):
        if self.request.user:
            current_service = self.get_object()
            if current_service.votes.filter(user=self.request.user).exists():
                return Response({'detail': _("Already voted.")}, status=status.HTTP_400_BAD_REQUEST)
            vote = current_service.votes.create(
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


class ServicePromotionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Services Promotions
    TODO permissions
    """

    PAGE_SIZE = 6

    queryset = ServicePromotion.objects
    serializer_class = ServicePromotionSerializer
    permission_classes = (IsOwnerOrReadOnly, )
    filter_backends = (filters.SearchFilter,
                       django_rest_filters.DjangoFilterBackend, )
    search_fields = ()
    filter_fields = ('author', 'author__id', 'service',
                     'service__id', 'transaction_id')

    # one minute cache
    # @method_decorator(cache_page(60*1))
    # @method_decorator(vary_on_cookie)
    # def dispatch(self, *args, **kwargs):
    #     return super(self.__class__, self).dispatch(*args, **kwargs)

    def perform_create(self, serializer):
        # if self.request.user:
        #     serializer.save(author=self.request.user)
        # else:
        raise PermissionDenied()

    def filter_promotion_queryset(self, queryset, request):
        """
        Filter promotion queryset
        TODO: fix filter logic
        """
        category = request.GET.get('category')
        query = request.GET.get('search')
        author_id = request.GET.get('author_id')
        location_id = request.GET.get('location_id')
        tags = request.GET.getlist('tags')

        queryset = queryset.filter(service__promoted_til__gte=timezone.now())

        condition = Q()

        if author_id:
            condition.add(Q(service__author_id=author_id), Q.AND)

        if category:
            # filter service category
            # Always change queryset
            condition.add(Q(service__category__name__iexact=category), Q.AND)

        condition2 = Q()
        if tags:
            # at least one tag from tags
            # do not change queryset if there are no services with tags
            condition2.add(Q(service__tags__name__in=tags), Q.OR)

        if query:
            # filter service title
            # do not change queryset if there are no services with similar title
            condition2.add(Q(service__title__icontains=query), Q.OR)
            condition2.add(Q(service__description__icontains=query), Q.OR)
            condition2.add(Q(service__tags__name__iexact=query), Q.OR)

        if location_id:
            condition2.add(Q(service__location_id=location_id), Q.OR)

        condition.add(condition2, Q.AND)

        return queryset.filter(condition)

    def list(self, request):
        """Custom list processing"""
        queryset = self.filter_promotion_queryset(self.queryset, request).distinct('id')
        # [:6]

        valid_id_list = list(queryset.values_list('id', flat=True))
        random_id_list = random.sample(valid_id_list, min(len(valid_id_list), self.PAGE_SIZE))
        queryset = self.queryset.filter(id__in=random_id_list)[:self.PAGE_SIZE]

        serializer = self.serializer_class(
            queryset, many=True, context={'request': request})

        return Response({
            'next': None,
            'previous': None,
            'count': 5,
            'pages': 1,
            'page': 1,
            'results': serializer.data
        })
