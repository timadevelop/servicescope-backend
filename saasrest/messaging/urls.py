"""
Messaging views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'conversations', views.ConversationViewSet, base_name="conversation")
ROUTER.register(r'messages', views.MessageViewSet, base_name="message")
ROUTER.register(r'message-images', views.MessageImageViewSet, base_name="messageimage")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
