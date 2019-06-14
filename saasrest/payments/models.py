import uuid

from django.db import models

from django.utils import timezone
from authentication.models import User


class Coupon(models.Model):
    """Coupon model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    DURATION_CHOICES = [
        ('once', 'once'),
        ('forever', 'forever'),
    ]
    duration = models.CharField(
        max_length=7,
        choices=DURATION_CHOICES,
        default='once'
    )

    # if user is set - coupon is only for this user
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="coupons", null=True, blank=True)
    # max times coupon can be used
    max_redemptions = models.PositiveSmallIntegerField(default=1)
    # number of times coupon has been applied
    times_redeemed = models.PositiveSmallIntegerField(default=0)
    # last datetime coupon is valid
    redeem_by = models.DateTimeField()
    # coupon creation datetime
    created_at = models.DateTimeField(auto_now_add=True)

    # promotion_days
    days = models.PositiveSmallIntegerField(default=5)

    @property
    def valid(self):
        """Is valid"""
        return self.times_redeemed < self.max_redemptions and \
            (self.duration == 'forever' or self.redeem_by > timezone.now())

    def redeem(self):
        """Redeem coupon"""
        self.times_redeemed += 1
        self.save(update_fields=['times_redeemed'])