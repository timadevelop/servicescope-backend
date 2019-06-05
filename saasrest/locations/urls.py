"""
Categories views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'locations', views.LocationViewSet, base_name="location")
ROUTER.register(r'districts', views.DistrictViewSet, base_name="district")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
