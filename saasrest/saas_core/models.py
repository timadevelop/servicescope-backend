from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from saas_core.images_compression import compress_image

# Create your models here.

class Image(models.Model):
    """Generic Image model"""
    # Below the mandatory fields for generic relation
    # REQUIREMENT: object have to provide likes & dislikes properties    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='images')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    image = models.ImageField(upload_to='images/%Y/%m/%d')

    __original_image = None

    def __init__(self, *args, **kwargs):
        super(Image, self).__init__(*args, **kwargs)
        self.__original_image = self.image

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Compress on save"""
        if not self.id or self.image != self.__original_image:
            self.image = compress_image(self.image)
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)
        self.__original_image = self.image


@receiver(post_delete, sender=Image)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)
