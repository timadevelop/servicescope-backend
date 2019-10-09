from django.contrib.admin.options import get_content_type_for_model
from django.utils.translation import ugettext as _
from rest_framework import serializers

from authentication.serializers import serialize_simple_user
from categories.models import Category
from locations.serializers import LocationSerializer
from saas_core.serializers import CreatableSlugRelatedField
from saas_core.utils import cached_or_new
from tags.models import Tag
from votes.serializers import VoteSerializer

from .models import Seeking, SeekingPromotion

from saas_core.models import Image
from saas_core.serializers import ImageSerializer

class SeekingSerializer(serializers.HyperlinkedModelSerializer):
    """Seeking serializer"""
    images = ImageSerializer(
        many=True,
        read_only=True)

    # likes = VoteSerializer(many=True, read_only=True)
    # dislikes = VoteSerializer(many=True, read_only=True)

    tags = CreatableSlugRelatedField(
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
        model = Seeking
        fields = ('id', 'url', 'author', 'title', 'description', 'max_price', 'max_price_currency', 'contact_phone', 'color', 'location',
                  'images', 'promoted_til', 'is_promoted', 'created_at', 'updated_at',
                  'tags', 'category', 'score', 'current_user_vote')
        
        read_only_fields = ('id', 'url', 'created_at', 'updated_at', 'author',
                            'images', 'score', 'current_user_vote')
        required_fields = ('title', 'description', 'location')
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def get_current_user(self):
        """Get current user"""
        user = None
        request = self.context.get("request")
        if request.user.is_authenticated:
            return request.user
        return None

    def validate_author(self, value):
        """Validate author field"""
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError(_("Login please"))

        user = request.user

        if user.id != value.id:
            raise serializers.ValidationError(
                _("You can not create seekings for another user"))

        return value

    def create(self, validated_data):
        seeking = super().create(validated_data)
        # create images
        image_data = self.context.get('view').request.FILES
        for img in image_data.values():
            img = Image.objects.create(content_object=seeking, image=img)
        return seeking

    def update(self, instance, validated_data):
        seeking = super().update(instance, validated_data)
        # append images on update
        image_data = self.context.get('view').request.FILES
        for img in image_data.values():
            img = Image.objects.create(content_object=seeking, image=img)
        return seeking

    def to_representation(self, instance, override=True):
        response = super().to_representation(instance)
        if self.context['request'] and override:
            if not isinstance(self.instance, list):
                # serialize author only for detailed-view
                response['author'] = serialize_simple_user(
                    user_id=instance.author_id, many=False, context=self.context)

            # serialize tags and location
            response['tags'] = [{'name': tag.name, 'color': tag.color}
                                for tag in instance.tags.all()]
            response['location'] = cached_or_new('SERIALIZED_LOCATION_{}'.format(
                instance.location_id), LocationSerializer, instance, 'location', self.context)

        return response


class ShortSeekingSerializer(SeekingSerializer):
    """Short seeking image serializer"""

    def to_representation(self, instance):
        response = super().to_representation(instance, False)
        if self.context['request']:
            # serialize tags and location
            response['tags'] = [{'name': tag.name, 'color': tag.color}
                                for tag in instance.tags.all()]
            response['location'] = cached_or_new('SERIALIZED_LOCATION_{}'.format(
                instance.location_id), LocationSerializer, instance, 'location', self.context)
        return response


class SeekingPromotionSerializer(serializers.HyperlinkedModelSerializer):
    """Seeking promotion serializer"""
    class Meta:
        model = SeekingPromotion
        fields = ('id', 'url', 'author', 'seeking', 'end_datetime', 'stripe_payment_intents',
                  'created_at', 'updated_at', 'is_valid', )
        read_only_fields = ('id', 'url', 'seeking',
                            'end_datetime', 'stripe_payment_intents', )
        required_fields = ()
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if self.context['request']:
            response['seeking'] = ShortSeekingSerializer(
                instance.seeking, many=False, context=self.context).data
        return response
