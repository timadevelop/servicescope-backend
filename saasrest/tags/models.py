"""Tags models"""
from django.core.cache import cache
from django.db import models
from colorfield.fields import ColorField

import random


TAG_COLORS = [
    '#ef6c57',
    '#8fbbaf',
    '#7ed3b2',
    '#caabd8',
    '#87a8d0',
    '#b9ceeb',
    '#f7d3ba',
    '#dfd3c3',
    '#c7b198',
]


def random_color():
    return random.choice(TAG_COLORS)


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
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
