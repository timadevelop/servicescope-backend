"""
Messaging views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'config', views.ConfigViewSet, base_name="public_config")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
