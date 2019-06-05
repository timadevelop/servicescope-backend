"""Tags models"""
from django.db import models
from colorfield.fields import ColorField

class Tag(models.Model):
    """Tag model"""
    name = models.TextField(max_length=20, blank=False,
                            null=False, unique=True)
    color = ColorField(max_length=10, default='#686de0')

    def __str__(self):
        return 'Tag[id: {id}, name: {name}]'.format(id=self.id, name=self.name)
