"""Tags models"""
from django.db import models
from colorfield.fields import ColorField

import random

TAG_COLORS = ['#40407a', '#706fd3', '#34ace0', '#227093',
              '#218c74', '#ff5252', '#b33939', '#ff793f', '#ffb142', '#D6A2E8']


def random_color():
    return random.choice(TAG_COLORS)

class Tag(models.Model):
    """Tag model"""
    name = models.TextField(max_length=20, blank=False,
                            null=False, unique=True)
    color = ColorField(max_length=10, default=random_color)

    def __str__(self):
        return 'Tag[id: {id}, name: {name}]'.format(id=self.id, name=self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        return super(Tag, self).save(*args, **kwargs)