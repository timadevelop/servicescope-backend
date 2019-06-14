from django.contrib.admin.options import get_content_type_for_model
from rest_framework import serializers

from authentication.serializers import UserSerializer
from categories.models import Category
from locations.serializers import LocationSerializer
from saas_core.utils import cached_or_new
from tags.models import Tag
from tags.serializers import TagSerializer
from votes.serializers import VoteSerializer

from .models import Service, ServiceImage, ServicePromotion
from django.utils.translation import ugettext as _


class ServiceImageSerializer(serializers.HyperlinkedModelSerializer):
    """Service image serializer"""
    class Meta:
        model = ServiceImage
        fields = ('service', 'image', )
        read_only_fields = ()
        required_fields = ('service', 'image', )
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def get_image(self, data):
        """TODO"""
        request = self.context.get('request')
        imageurl = data.image.url
        return request.build_absolute_uri(imageurl)


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    """Service serializer"""
    images = ServiceImageSerializer(
        many=True,
        read_only=True)

    # likes = VoteSerializer(many=True, read_only=True)
    # dislikes = VoteSerializer(many=True, read_only=True)

    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects,
        slug_field='name'
    )

    category = serializers.SlugRelatedField(
        many=False,
        queryset=Category.objects,
        slug_field='name'
    )

    current_user_vote = serializers.SerializerMethodField()

    def get_current_user_vote(self, instance):
        """Current user vote on serialization"""
        user = self.get_current_user()
        if not user or user.is_anonymous:
            return None

        if not isinstance(self.instance, list):
            # just one instance
            try:
                vote = instance.votes.get(user__id=user.id)
                if vote:
                    return VoteSerializer(vote, many=False, context=self.context).data
            except:
                return None
        else:
            # we are processing a list (it's better to reduce some sql queries)
            user_instances_votes = self.context.get(
                'user_instances_votes', None)
            if user_instances_votes is None:
                content_type = get_content_type_for_model(instance)
                votes_list = list(user.votes.filter(content_type=content_type,
                                                    object_id__in=[i.pk for i in self.instance]))
                self.context["user_instances_votes"] = {
                    v.object_id: v for v in votes_list}
                user_instances_votes = self.context["user_instances_votes"]

            vote = user_instances_votes.get(instance.id, None)
            if vote:
                return VoteSerializer(vote, many=False, context=self.context).data

        return None

    class Meta:
        model = Service
        fields = ('id', 'url', 'author', 'title', 'description', 'price', 'price_currency',
                  'contact_phone', 'contact_email', 'color', 'location',
                  'images',
                  'promoted_til',
                  'is_promoted',
                  'created_at', 'updated_at',
                  'tags', 'category', \
                  # 'promotions', \
                  # 'likes', 'dislikes', \
                  'score', 'current_user_vote', 'price_details')
        read_only_fields = ('id', 'url', 'created_at', 'updated_at', 'author',
                            'images', 'promotions',
                            # 'likes', 'dislikes', \
                            'score', 'current_user_vote')
        required_fields = ('title', 'description', 'price',
                           'price_currency', 'location')
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def get_current_user(self):
        """Get current user"""
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            return request.user
        return None

    def validate_author(self, value):
        """Validate author field"""
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError(_("Login please"))

        user = request.user

        if user != value:
            raise serializers.ValidationError(_("You can not create services for another user"))

        return value

    def create(self, validated_data):
        service = super().create(validated_data)
        image_data = self.context.get('view').request.FILES
        for img in image_data.values():
            img = ServiceImage.objects.create(service=service, image=img)
        return service

    def update(self, instance, validated_data):
        service = super().update(instance, validated_data)
        image_data = self.context.get('view').request.FILES
        for img in image_data.values():
            img = ServiceImage.objects.create(service=service, image=img)
        return service

    def to_representation(self, instance, override=True):
        response = super().to_representation(instance)
        if self.context['request'] and override:
            if not isinstance(self.instance, list):
                response['author'] = UserSerializer(
                    instance.author, many=False, context=self.context).data

            # response['images'] = ServiceImageSerializer(
            # instance.images, many=True, context = self.context).data

            # response['category'] = CategorySerializer(
            # instance.category, many=False, context = self.context).data

            response['tags'] = TagSerializer(
                instance.tags, many=True, context=self.context).data
            response['location'] = cached_or_new('SERIALIZED_LOCATION_{}'.format(
                instance.location_id), LocationSerializer, instance, 'location', self.context)

            # response['location'] = LocationSerializer(
            # instance.location, many=False, context = self.context).data
        return response


class ShortServiceSerializer(ServiceSerializer):
    """Short service image serializer"""

    def to_representation(self, instance):
        response = super().to_representation(instance, False)
        if self.context['request']:
            response['tags'] = TagSerializer(
                instance.tags, many=True, context=self.context).data
            response['location'] = cached_or_new('SERIALIZED_LOCATION_{}'.format(
                instance.location_id), LocationSerializer, instance, 'location', self.context)
        return response


class ServicePromotionSerializer(serializers.HyperlinkedModelSerializer):
    """Service promotion serializer"""
    class Meta:
        model = ServicePromotion
        fields = ('id', 'url', 'author', 'service', 'end_datetime', 'stripe_payment_intents',
                  'created_at', 'updated_at', 'is_valid', )
        read_only_fields = ('id', 'url', 'service', 'end_datetime', 'stripe_payment_intents', )
        required_fields = ()
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if self.context['request']:
            # response['author'] = UserSerializer(instance.author,
            # many=False, context = self.context).data
            response['service'] = ShortServiceSerializer(
                instance.service, many=False, context=self.context).data
        return response
