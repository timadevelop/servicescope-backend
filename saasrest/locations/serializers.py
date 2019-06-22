from django.core.cache import cache
from rest_framework import serializers

from .models import District, Location


class DistrictSerializer(serializers.HyperlinkedModelSerializer):
    """Location Serializer"""
    class Meta:
        model = District
        fields = ('id', 'url', 'name', 'oblast',
                  # 'ekatte',
                  # 'region',
                  )
        read_only_fields = fields
        lookup_field = 'oblast'
        extra_kwargs = {
            'url': {'lookup_field': 'oblast'}
        }


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    """Location Serializer"""
    class Meta:
        model = Location
        fields = ('id', 'url',
                  't_v_m', 'name',
                  #   'oblast', 'ekatte',
                  #   'obstina', 'kmetstvo', 'kind', 'category', 'altitude'
                  )
        read_only_fields = fields

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if self.context['request']:
            district_data = cache.get(
                'SERIALIZED_DISTRICT_{}'.format(instance.oblast))
            if district_data is None:
                district = District.objects.get(oblast=instance.oblast)
                district_data = DistrictSerializer(
                    district, many=False, context=self.context).data
                cache.set('SERIALIZED_DISTRICT_{}'.format(
                    instance.oblast), district_data)

            response['district'] = district_data
        return response
