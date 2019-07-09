"""
Messaging views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'services', views.ServiceViewSet, base_name="service")
ROUTER.register(r'service-promotions', views.ServicePromotionViewSet, base_name="servicepromotion")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
