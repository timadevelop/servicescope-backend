from djmoney.models.fields import MoneyField
from colorfield.fields import ColorField
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now

from authentication.models import User
from categories.models import Category
from locations.models import Location
from tags.models import Tag
from votes.models import Vote

from saas_core.models import Image

import logging
logger = logging.getLogger(__name__)

class Seeking(models.Model):
    """Seeking model"""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='seekings')

    title = models.TextField(max_length=100, blank=False)
    description = models.TextField(max_length=900, blank=True)

    tags = models.ManyToManyField(Tag, related_name='seekings')
    category = models.ForeignKey(
        Category, related_name='seekings', null=True, blank=True, on_delete=models.SET_NULL)

    contact_phone = models.TextField(max_length=30, blank=True)

    color = ColorField(max_length=10, default='#686de0')

    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    score = models.IntegerField(default=0)
    votes = GenericRelation(Vote)
    images = GenericRelation(Image)
    max_price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    promoted_til = models.DateTimeField(null=True, blank=True)

    def likes(self):
        return self.votes.filter(activity_type=Vote.UP_VOTE)

    def dislikes(self):
        return self.votes.filter(activity_type=Vote.DOWN_VOTE)

    @property
    def is_promoted(self):
        if self.promoted_til and self.promoted_til > now():
            return True
        return False

    def get_absolute_url(self):
        return reverse('seeking-detail', args=[str(self.id)])

    def promote(self, user, intent_id, days):
        logger.info('Trying to promote seek #{}, intent_id: {}'.format(self.pk, intent_id))

        current_datetime = timezone.now()
        if self.promotions.exists():
            logger.info('Updating old promotion')
            seeking_promotion = self.promotions.order_by('-end_datetime').first()

            # add days
            countdown_datetime = seeking_promotion.end_datetime if seeking_promotion.end_datetime < current_datetime else current_datetime
            seeking_promotion.end_datetime = countdown_datetime + \
                timezone.timedelta(days=days)

            if intent_id:
                seeking_promotion.stripe_payment_intents.append(intent_id)
            try:
                seeking_promotion.save()
            except Exception as e:
                logger.error(str(e))
            else:
                logger.info('Successfully updated old promotion')            
        else:
            logger.info('Creating new promotion')
            end_datetime = timezone.now() + timezone.timedelta(days=days)
            try:
                seeking_promotion = SeekingPromotion.objects.create(
                    author=user, seeking=self,
                    stripe_payment_intents=[intent_id],
                    end_datetime=end_datetime)
            except Exception as e:
                logger.error(str(e))
            else:
                logger.info("Successfully created new promotion")

        logger.info("Updating seek.promoted_til field...")
        try:
            self.promoted_til = seeking_promotion.end_datetime
            self.save()
        except Exception as e:
            logger.error("Error while updating promoted_til field: {}".format(str(e)))
        else:
            logger.info("Successfully changed promoted_til field")


        logger.info("Successfully promoted seek #{} til {}".format(self.pk, str(self.promoted_til)))
        return seeking_promotion


class SeekingPromotion(models.Model):
    """Seeking promotion"""
    author = models.ForeignKey(User, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='seeking_promotions')
    seeking = models.ForeignKey(
        Seeking, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions')

    end_datetime = models.DateTimeField(blank=False, null=False)

    stripe_payment_intents = ArrayField(models.CharField(max_length=110))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_valid(self):
        """is valid promotion"""
        return self.end_datetime > now()
