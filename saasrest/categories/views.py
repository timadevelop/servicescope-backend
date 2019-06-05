"""Views"""
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Category
from .serializers import CategorySerializer


# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    """Category viewset"""
    queryset = Category.objects.order_by('-name')
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('name', )

    @method_decorator(cache_page(60*1))
    def dispatch(self, request, *args, **kwargs):
        """Cache"""
        return super(CategoryViewSet, self).dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        if self.request.user:
            serializer.save()
        else:
            raise PermissionDenied()

    @action(detail=False, methods=['get'], url_path='name/(?P<category_name>[^/]+)')
    def get_category_by_name(self, request, category_name):
        """
        Get category by name endpoint
        """
        try:
            category = self.queryset.get(name=category_name)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(category, many=False, context={'request': request})
        return Response(serializer.data)
