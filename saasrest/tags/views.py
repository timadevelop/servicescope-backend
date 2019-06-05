"""Tags views"""

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as django_rest_filters
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Tag
from .serializers import TagSerializer


# pylint: disable=too-many-ancestors
class TagViewSet(viewsets.ModelViewSet):
    """
    Tags viewset
    """
    queryset = Tag.objects.order_by('-name')
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (filters.SearchFilter,
                       django_rest_filters.DjangoFilterBackend, )
    search_fields = ('name', )

    @method_decorator(cache_page(60*1))
    def dispatch(self, request, *args, **kwargs):
        return super(TagViewSet, self).dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        if self.request.user:
            serializer.save()
        else:
            raise PermissionDenied()

    @action(detail=False, methods=['get'], url_path='name/(?P<tag_name>[^/]+)')
    def get_tag_by_name(self, request, tag_name):
        """
        Endpoint for getting a tag by name (.../name/<tag name>)
        """
        try:
            tag = self.queryset.get(name=tag_name)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            tag, many=False, context={'request': request})
        return Response(serializer.data)
