"""Models"""
from django.db import models

from authentication.models import User

from django.utils.translation import ugettext as _
from django.contrib.contenttypes.fields import GenericRelation

from saas_core.models import Image


class Conversation(models.Model):
    """Conversation"""
    title = models.TextField(max_length=30, blank=False)
    # related messages field
    # TODO: rm from users current user on response
    users = models.ManyToManyField(User, related_name="conversations")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    """Message"""
    author = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name='messages')

    conversation = models.ForeignKey(
        Conversation,
        null=False,
        on_delete=models.CASCADE,
        related_name='messages')

    text = models.TextField(max_length=1000, blank=True)

    images = GenericRelation(Image)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_text(self):
        # TODO: rm null
        if not self.text or self.text == 'null':
            return "{} {}".format(self.author.first_name, _("sent you attachment"))
        else:
            return self.text
