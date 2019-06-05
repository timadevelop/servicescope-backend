"""Votes serializers"""
from rest_framework import serializers
from .models import Vote


class VoteSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for Vote instances. """
    class Meta:
        model = Vote
        fields = ('id', 'url', 'user', 'activity_type', 'date')
