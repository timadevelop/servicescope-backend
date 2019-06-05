"""
Messaging views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'notifications', views.NotificationViewSet, base_name="notification")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
