"""Tags serializers"""
from rest_framework import serializers
from .models import Tag

class TagSerializer(serializers.HyperlinkedModelSerializer):
    """Tag serializer"""
    class Meta:
        model = Tag
        fields = ('name', 'color')
        read_only_fields = ()
        required_fields = ('name',)
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def validate_name(self, value):
        return value.lower()