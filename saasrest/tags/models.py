"""Tags models"""
from django.core.cache import cache
from django.db import models
from colorfield.fields import ColorField

import random

TAG_COLORS = ['#40407a', '#706fd3', '#34ace0', '#227093',
              '#218c74', '#ff5252', '#b33939', '#ff793f', '#ffb142', '#D6A2E8']


def random_color():
    return random.choice(TAG_COLORS)


def get_serialized_tag_cache_key(tag_id):
    """Cache key for serialized tag"""
    return 'TAGS_SERIALIZED_TAG_{}'.format(tag_id)


class LowerTextField(models.TextField):

    def get_prep_value(self, value):
        return str(value).lower()


class Tag(models.Model):
    """Tag model"""
    name = LowerTextField(max_length=20, blank=False,
                          null=False, unique=True)
    color = ColorField(max_length=10, default=random_color)

    def __str__(self):
        return 'Tag[id: {id}, name: {name}]'.format(id=self.id, name=self.name)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # invalidate_cache
        cache.delete(get_serialized_tag_cache_key(self.pk))
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
