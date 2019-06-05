"""
Messaging views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'payments', views.PaymentsViewSet, base_name="payment")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
