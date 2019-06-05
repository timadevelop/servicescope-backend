"""
Serializers
"""
from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """Category Serializer"""
    class Meta:
        """Meta"""
        model = Category
        fields = ('name', 'color')
        read_only_fields = ()
        required_fields = ('name',)
        extra_kwargs = {field: {'required': True} for field in required_fields}
