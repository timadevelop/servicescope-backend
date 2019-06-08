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

    def get_notifications_count(self, instance):
        return instance.notifications.filter(notified=False).count()

    class Meta:
        model = User
        # TODO
        fields = ('id', 'url', 'email', 'phone', 'bio', 'first_name', 'last_name', 'image', 'date_joined', )
        read_only_fields = ('id', 'url', )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            if not isinstance(self.instance, list):
                response['services_count'] = self.get_services_count(instance)
                response['posts_count'] = self.get_posts_count(instance)
                # response['income_reviews_count'] = self.get_income_reviews_count(
                # instance)
                # response['offers_count'] = self.get_offers_count(instance)
                response['notifications_count'] = self.get_notifications_count(
                    instance)

        return response


class PrivateUserSerializer(serializers.HyperlinkedModelSerializer):
    """
    User serializer with private info
    """
    class Meta:
        model = User
        # TODO
        fields = ('id', 'url', 'email', 'phone', 'bio', 'first_name', 'last_name',
                  'service_promotions', 'services', 'is_verified_email',)
        # outcome_reviews, income_reviwes
        read_only_fields = ('id', 'url', )
