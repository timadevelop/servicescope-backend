"""Feed models"""
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from authentication.models import User
from saas_core.images_compression import compress_image
from tags.models import Tag
from votes.models import Vote


class FeedPost(models.Model):
    """FeedPost model"""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='feed_posts')

    text = models.TextField(max_length=1000, blank=True)
    tags = models.ManyToManyField(Tag, related_name='feed_posts')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    score = models.IntegerField(default=0)
    votes = GenericRelation(Vote)
    
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

class FeedPostImage(models.Model):
    """FeedPost image"""
    feed_post = models.ForeignKey(
        FeedPost, on_delete=models.CASCADE, null=False, related_name='images')
    image = models.ImageField(upload_to='images/feed_posts/%Y/%m/%d')

    def save(self, *args, **kwargs):
        """Compress on save"""
        if self.image:
            self.image = compress_image(self.image)
        super().save(*args, **kwargs)

@receiver(post_delete, sender=FeedPostImage)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
