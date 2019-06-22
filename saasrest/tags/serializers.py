"""Tags serializers"""
from rest_framework import serializers
from .models import Tag

class TagSerializer(serializers.HyperlinkedModelSerializer):
    """Tag serializer"""
    class Meta:
        model = Tag
        fields = ('name', 'color')
        read_only_fields = ('color', )
        required_fields = ('name', )
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def validate_name(self, value):
        return value.lower()

def serialize_tag(tags, many=False):
    def serialize(tag):
        return {
            'name': tag.name,
            'color': tag.color
        }
    if many:
        return map(serialize, tags.all())
    
    return serialize(tags)