"""
Messaging views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'feed', views.FeedPostViewSet, base_name="feedpost")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
