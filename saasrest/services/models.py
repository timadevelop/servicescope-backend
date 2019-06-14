from colorfield.fields import ColorField
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.utils.timezone import now

from authentication.models import User
from categories.models import Category
# pylint: disable=fixme, import-error
from djmoney.models.fields import MoneyField
from locations.models import Location
from tags.models import Tag
from votes.models import Vote

from django.utils import timezone

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


    def promote(self, user, intent_id, days):
        if self.promotions.exists():
            print('update old promotion')
            service_promotion = self.promotions.first()
            # add days
            service_promotion.end_datetime = service_promotion.end_datetime + \
                timezone.timedelta(days=days)
            
            if intent_id:
                service_promotion.stripe_payment_intents.append(intent_id)
            service_promotion.save()
            print('success')
        else:
            print('create new promotion')
            end_datetime = timezone.now() + timezone.timedelta(days=days)
            service_promotion = ServicePromotion.objects.create(
                author=user, service=self,
                stripe_payment_intents=[intent_id],
                end_datetime=end_datetime)
            print('success')

        self.promoted_til = service_promotion.end_datetime
        self.save()

        return service_promotion


class ServiceImage(models.Model):
    """Service image"""
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, null=False, related_name='images')
    image = models.ImageField(upload_to='images/services/%Y/%m/%d')


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
