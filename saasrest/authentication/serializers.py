from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer

from django.core.cache import cache

from .models import User, get_serialized_user_cache_key


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



def serialize_user_instance(user, context):
    request = context.get('request')
    if not user:
        return None
    result = {
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
    return result

def get_user(user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None

def serialize_simple_user(user_id=None, user=None, users=None, many=False, context=None):
    def serialize(user):
        return serialize_user_instance(user, context)
    if user_id:
        key = get_serialized_user_cache_key(user_id)

        # get from context
        serialized_user = context.get(key)
        if serialized_user:
            return serialized_user
        
        serialized_user = cache.get(key)
        if serialized_user:
            context[key] = serialized_user
            return serialized_user

        # serialize
        if not user:
            user = get_user(user_id)
        serialized_user = serialize_user_instance(user, context)

        if serialized_user:
            # save
            if not cache.has_key(key):
                cache.set(key, serialized_user)
            if key not in context:
                context[key] = serialized_user

        return serialized_user
    elif many:
        if users is None:
            return None
        return map(serialize, users.all())
    else:
        return serialize_user_instance(user, context)


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
