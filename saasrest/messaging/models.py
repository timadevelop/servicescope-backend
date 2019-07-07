"""Models"""
from django.db import models

from authentication.models import User

from django.utils.translation import ugettext as _

from saas_core.images_compression import compress_image

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
    # related images field

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_text(self):
        # TODO: rm null
        if not self.text or self.text == 'null':
            return "{} {}".format(self.author.first_name, _("sent you attachment"))
        else:
            print(self.text)
            return self.text


class MessageImage(models.Model):
    """Message Image"""
    message = models.ForeignKey(Message,
                                on_delete=models.CASCADE,
                                null=False,
                                related_name='images')
    image = models.ImageField(upload_to='images/messages/%Y/%m/%d')
    __original_image = None

    def __init__(self, *args, **kwargs):
        super(MessageImage, self).__init__(*args, **kwargs)
        self.__original_image = self.image

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Compress on save"""
        if self.image and self.image != self.__original_image:
            self.image = compress_image(self.image)
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)
        self.__original_image = self.image