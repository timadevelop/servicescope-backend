"""
Messaging views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'votes', views.VoteViewSet, base_name="vote")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
