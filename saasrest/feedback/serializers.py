from rest_framework import serializers

from .models import Feedback

class FeedbackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Feedback
        fields = ('id', 'url', 'author', 'rate', 'text', 'created_at')
        read_only_fields = ('id', 'url', 'author', 'created_at')
        required_fields = ('rate', 'text')
        extra_kwargs = {field: {'required': True} for field in required_fields}

