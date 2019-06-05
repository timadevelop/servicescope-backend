"""
Authentication views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'users', views.UserViewSet, base_name="user")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
