"""
Saas core url
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'images', views.ImageViewSet, base_name="image")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
