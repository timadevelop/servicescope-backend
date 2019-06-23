"""Tags serializers"""
from django.core.cache import cache
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


def get_serialized_tag_cache_key(tag_id):
    """Cache key for serialized tag"""
    return 'TAGS_SERIALIZED_TAG_{}'.format(tag_id)


def serialize_tag(tags, tag_id=None, many=False):
    """Simple tag serialization"""
    def serialize(tag_id):
        key = get_serialized_tag_cache_key(tag_id)
        serialized_tag = cache.get(key)
        if not serialized_tag:
            tag = Tag.objects.get(pk=tag_id)
            serialized_tag = {
                'name': tag.name,
                'color': tag.color
            }
            cache.set(get_serialized_tag_cache_key(tag_id), serialized_tag)
        return serialized_tag
    if many:
        return map(serialize, tags.values_list('id', flat=True))
    elif tag_id:
        return serialize(tag_id)
    return None
