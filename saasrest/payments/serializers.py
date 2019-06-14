"""Payments serializers"""
from rest_framework import serializers

from .models import Coupon


class CouponSerializer(serializers.HyperlinkedModelSerializer):
    """Coupon Serializer"""
    class Meta:
        model = Coupon
        fields = ('id', 'url', 'duration', 'user', 'max_redemptions',
                  'times_redeemed', 'redeem_by', 'created_at', 'valid')
        read_only_fields = ('id', 'times_redeemed', 'created_at', 'valid')
