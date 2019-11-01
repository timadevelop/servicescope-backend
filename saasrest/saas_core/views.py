from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Image
from .permissions import IsOwnerOrReadOnly
from .serializers import ImageSerializer

from saas_core.config import DEFAULT_PERMISSION_CLASSES

class ImageViewSet(viewsets.ModelViewSet):
    """
    Service image viewset
    TODO
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = DEFAULT_PERMISSION_CLASSES + [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, ]
