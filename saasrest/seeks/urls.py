"""
Messaging views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'seekings', views.SeekingViewSet, base_name="seeking")
ROUTER.register(r'seeking-promotions', views.SeekingPromotionViewSet, base_name="seekingpromotion")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
