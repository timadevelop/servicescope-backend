"""
Categories views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'categories', views.CategoryViewSet, base_name="category")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
