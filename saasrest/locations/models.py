"""Models"""
from django.db import models

# Create your models here.


class District(models.Model):
    """District model"""
    oblast = models.TextField(max_length=5, blank=False, null=False)
    ekatte = models.TextField(max_length=5, blank=False, null=False)

    name = models.TextField(max_length=100, null=False, blank=False)
    region = models.TextField(max_length=5, blank=False, null=False)

    def __str__(self):
        return "District #{} : {}".format(self.id, self.oblast)


class Location(models.Model):
    """Location model"""
    ekatte = models.TextField(max_length=5, blank=False, null=False)
    t_v_m = models.TextField(max_length=5, blank=False, null=False)
    name = models.TextField(max_length=100, null=False, blank=False)
    oblast = models.TextField(max_length=5, blank=False, null=False)
    obstina = models.TextField(max_length=5, blank=False, null=False)
    kmetstvo = models.TextField(max_length=10, blank=False, null=False)

    kind = models.PositiveSmallIntegerField(blank=False, null=False)
    category = models.PositiveSmallIntegerField(blank=False, null=False)
    altitude = models.PositiveSmallIntegerField(blank=False, null=False)
