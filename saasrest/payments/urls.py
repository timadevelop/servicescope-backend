"""
Messaging views
"""
from rest_framework import routers
from django.conf.urls import url, include
from . import views

ROUTER = routers.DefaultRouter()
ROUTER.register(r'payments', views.PaymentsViewSet, base_name="payment")
ROUTER.register(r'coupons', views.CouponViewSet, base_name="coupon")

urlpatterns = [
    url(r'', include(ROUTER.urls))
]
