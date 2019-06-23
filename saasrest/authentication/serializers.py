from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer

from .models import User

# from asgiref.sync import async_to_sync
# from django.db.models.signals import post_save, post_delete

# from django.dispatch import receiver

# from django.urls import resolve

# from django.db.models import Q

# from datetime import datetime
# from saasrest.settings import REST_FRAMEWORK


class CustomRegisterSerializer(RegisterSerializer):
    """
    User serializer on registration process
    """
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    bio = serializers.CharField(
        max_length=500, required=False, allow_blank=True)
    phone = serializers.CharField(
        max_length=100, required=False, allow_blank=True)

    def get_cleaned_data(self):
        # super(CustomRegisterSerializer, self).get_cleaned_data()

        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone': self.validated_data.get('phone', ''),
            'bio': self.validated_data.get('bio', ''),
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            bio=validated_data['bio'],
        )
        return user

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    """
    wat
    """
    class Meta:
        model = User
        fields = ('email')
        read_only_fields = ('email',)


def serialize_simple_user(user, many=False, context=None):
    request = context.get('request')

    def serialize(user):
        return {
            'id': user.id,
            'url': request.build_absolute_uri(user.get_absolute_url()),
            'bio': user.bio,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'image': request.build_absolute_uri(user.image.url) if request and user.image else None,
            'date_joined': user.date_joined.isoformat(),
            'last_active': user.last_active.isoformat(),
            'is_online': user.is_online
        }
    if many:
        return map(serialize, user.all())
    return serialize(user)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Main user serializer
    """

    def get_services_count(self, instance):
        return instance.services.count()

    def get_posts_count(self, instance):
        return 0
        # return instance.posts.count()

    # def get_income_reviews_count(self, instance):
    #     return instance.income_reviews.count()

    # def get_offers_count(self, instance):
    #     return instance.offers.count()

    class Meta:
        model = User
        # TODO
        fields = ('id', 'url', 'bio', 'first_name', 'last_name',
                  'image', 'date_joined', 'last_active', 'is_online')
        read_only_fields = fields

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            if not isinstance(self.instance, list):
                response['services_count'] = self.get_services_count(instance)
                response['posts_count'] = self.get_posts_count(instance)
                # response['income_reviews_count'] = self.get_income_reviews_count(
                # instance)
                # response['offers_count'] = self.get_offers_count(instance)

        return response


class PrivateUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    User serializer with private info
    """
    notifications_count = serializers.SerializerMethodField()

    def get_notifications_count(self, instance):
        r = instance.notifications.count()
        return r

    class Meta:
        model = User
        # TODO
        fields = ('id', 'url', 'email', 'phone', 'bio', 'first_name', 'last_name', 'notifications_count',
                  'service_promotions', 'services', 'is_verified_email', 'image', 'last_active', 'is_online')
        # outcome_reviews, income_reviwes
        read_only_fields = ('id', 'url', 'is_online', 'last_active', 'is_verified_email',
                            'services', 'service_promotions', 'notifications_count',)
