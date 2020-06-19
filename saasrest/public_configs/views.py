"""Views for public configurations"""
from rest_framework import status, viewsets

from rest_framework.decorators import action
from rest_framework.response import Response

from django.conf import settings
from saas_core.config import DEFAULT_PERMISSION_CLASSES


class ConfigViewSet(viewsets.ViewSet):
    """
    Config
    # TODO:
    """
    @action(detail=False, methods=['get'], url_path='get_configuration', permission_classes=DEFAULT_PERMISSION_CLASSES)
    def get_configuration(self, request):
        """TODO"""
        resp = {
            'API_CLIENT_ID': settings.API_CLIENT_ID,
            'API_CLIENT_SECRET': settings.API_CLIENT_SECRET,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_TEST_PUBLIC_KEY,
            'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
            'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID,
        }

        return Response(resp)
