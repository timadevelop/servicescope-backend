"""Views"""
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import geocoder
from saas_core.permissions import IsAdminUserOrReadOnly

from .models import District, Location
from .serializers import DistrictSerializer, LocationSerializer


class LocationViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Location.objects.order_by('kind')
    serializer_class = LocationSerializer
    permission_classes = (IsAdminUserOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('name',)
    filter_fields = ()

    @method_decorator(cache_page(60*60*24*10))
    def dispatch(self, request, *args, **kwargs):
        return super(LocationViewSet, self).dispatch(request, *args, **kwargs)

    # create only for employee & customer.

    def perform_create(self, serializer):
        if self.request.user:
            serializer.save()
        else:
            raise PermissionDenied()

    @action(detail=False, methods=['get'], url_path='geo/(?P<geo_query>[^/]+)')
    def get_geo(self, request, geo_query):
        """geocoder api endpoint"""
        try:
            resp = geocoder.geonames(geo_query,
                                     country=['BG'],
                                     key='timadevelop',
                                     maxRows=10,
                                     lang='bg',
                                     # adm and cities / village
                                     featureClass=['P', 'A'],
                                     fuzzy=1.0)
            # isNameRequired=True)
            # name_startsWith=[geo_query],
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        result = [r.json for r in resp]
        return Response(result)


class DistrictViewSet(viewsets.ModelViewSet):
    """
    District viewset
    """
    queryset = District.objects.order_by('-id')
    serializer_class = DistrictSerializer
    permission_classes = (IsAuthenticated, IsAdminUserOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('name',)
    filter_fields = ()
    lookup_field = 'oblast'

    @method_decorator(cache_page(60*60*24*10))
    def dispatch(self, request, *args, **kwargs):
        return super(DistrictViewSet, self).dispatch(request, *args, **kwargs)

    # create only for employee & customer.
    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_admin:
            serializer.save()
        else:
            raise PermissionDenied()
