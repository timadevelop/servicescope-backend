"""
Messaging views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'tags', views.TagViewSet, base_name="tag")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
