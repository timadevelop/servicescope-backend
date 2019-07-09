from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Image
from .permissions import IsOwnerOrReadOnly
from .serializers import ImageSerializer


class ImageViewSet(viewsets.ModelViewSet):
    """
    Service image viewset
    TODO
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )
