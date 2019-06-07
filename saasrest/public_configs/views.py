"""Views for public configurations"""
from rest_framework import status, viewsets

from rest_framework.decorators import action
from rest_framework.response import Response

from saasrest import local_settings

class ConfigViewSet(viewsets.ViewSet):
    """
    Config
    # TODO:
    """
    @action(detail=False, methods=['get'], url_path='get_configuration', permission_classes = [])
    def get_configuration(self, request):
        """TODO"""
        resp = {
            'API_CLIENT_ID': local_settings.API_CLIENT_ID,
            'API_CLIENT_SECRET': local_settings.API_CLIENT_SECRET,
            'STRIPE_PUBLIC_KEY': local_settings.STRIPE_TEST_PUBLIC_KEY,
            'GOOGLE_CLIENT_ID': local_settings.GOOGLE_CLIENT_ID,
        }

        return Response(resp)
        