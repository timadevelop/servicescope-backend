"""Votes models"""
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from authentication.models import User


class Vote(models.Model):
    """Vote model"""
    FAVORITE = 'F'
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    ACTIVITY_TYPES = (
        (FAVORITE, 'Favorite'),
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, related_name='votes')
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)
    date = models.DateTimeField(auto_now_add=True)

    # Below the mandatory fields for generic relation
    # REQUIREMENT: object have to provide likes & dislikes properties
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()


@receiver(post_save, sender=Vote, dispatch_uid='vote_post_save_signal')
def update_obj_score(sender, instance, created, **kwargs):
    """
    Update object score on vote creation

    Object required to have likes & dislikes properties
    """
    if created:
        obj = instance.content_object
        obj.score = obj.likes().count() - obj.dislikes().count()
        obj.save(update_fields=['score'])


@receiver(post_delete, sender=Vote, dispatch_uid='vote_pre_delete_signal')
def change_obj_score(sender, instance, using, **kwargs):
    """
    Update object score on vote delete

    Object required to have likes & dislikes properties
    """
    obj = instance.content_object
    if obj:
        obj.score = obj.likes().count() - obj.dislikes().count()
        obj.save(update_fields=['score'])
