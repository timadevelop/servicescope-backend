from colorfield.fields import ColorField
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now

from authentication.models import User
from categories.models import Category
# pylint: disable=fixme, import-error
from djmoney.models.fields import MoneyField
from locations.models import Location
from saas_core.images_compression import compress_image
from tags.models import Tag
from votes.models import Vote


from saas_core.models import Image

import logging
logger = logging.getLogger(__name__)

class Service(models.Model):
    """Service model"""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='services')

    title = models.TextField(max_length=100, blank=False)
    description = models.TextField(max_length=900, blank=True)
    tags = models.ManyToManyField(Tag, related_name='services')
    category = models.ForeignKey(
        Category, related_name='services', null=True, blank=True, on_delete=models.SET_NULL)

    contact_phone = models.TextField(max_length=30, blank=True)
    contact_email = models.TextField(max_length=30, blank=True)

    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    price_details = JSONField(default=list)

    color = ColorField(max_length=10, default='#686de0')

    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    score = models.IntegerField(default=0)
    votes = GenericRelation(Vote)
    images = GenericRelation(Image)

    promoted_til = models.DateTimeField(null=True, blank=True)

    def likes(self):
        return self.votes.filter(activity_type=Vote.UP_VOTE)

    def dislikes(self):
        return self.votes.filter(activity_type=Vote.DOWN_VOTE)

    # hints
    # Get the post object
    #post = Post.objects.get(pk=1)
    # Add a like activity
    #post.likes.create(activity_type=Vote.LIKE, user=request.user)
    # Or in a similar way using the Activity model to add the like
    #Vote.objects.create(content_object=post, activity_type=Activity.LIKE, user=request.user)

    @property
    def is_promoted(self):
        if self.promoted_til and self.promoted_til > now():
            return True
        return False

    def get_absolute_url(self):
        return reverse('service-detail', args=[str(self.id)])

    def promote(self, user, intent_id, days):
        logger.info('Trying to promote service #{}, intent_id: {}'.format(self.pk, intent_id))

        current_datetime = timezone.now()
        if self.promotions.exists():
            logger.info('Updating old promotion')
            service_promotion = self.promotions.order_by('-end_datetime').first()

            countdown_datetime = service_promotion.end_datetime if service_promotion.end_datetime > current_datetime else current_datetime
            service_promotion.end_datetime = countdown_datetime + \
                timezone.timedelta(days=days)

            if intent_id:
                service_promotion.stripe_payment_intents.append(intent_id)

            try:
                service_promotion.save()
            except Exception as e:
                logger.error(str(e))
            else:
                logger.info('Successfully updated old promotion')
        else:
            logger.info('Creating new promotion')
            end_datetime = current_datetime + timezone.timedelta(days=days)
            try:
                service_promotion = ServicePromotion.objects.create(
                    author=user, service=self,
                    stripe_payment_intents=[intent_id],
                    end_datetime=end_datetime)
            except Exception as e:
                logger.error(str(e))
            else:
                logger.info("Successfully created new promotion")

        logger.info("Updating seek.promoted_til field...")
        try:
            self.promoted_til = service_promotion.end_datetime
            self.save()
        except Exception as e:
            logger.error("Error while updating promoted_til field: {}".format(str(e)))
        else:
            logger.info("Successfully changed promoted_til field")

        logger.info("Successfully promoted service #{} til {}".format(self.pk, str(self.promoted_til)))
        return service_promotion


class ServicePromotion(models.Model):
    """Service promotion"""
    author = models.ForeignKey(User, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='service_promotions')
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions')

    end_datetime = models.DateTimeField(blank=False, null=False)

    stripe_payment_intents = ArrayField(models.CharField(max_length=110))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_valid(self):
        """is valid promotion"""
        return self.end_datetime > now()
