from rest_framework import serializers
from .models import User, Notification, Review, \
    District, Location, Tag, Category, \
    Service, ServiceImage, ServicePromotion, \
    Post, PostImage, PostPromotion, Offer, Vote

from django.urls import resolve

from django.db.models import Q

from datetime import datetime
from saasrest.settings import REST_FRAMEWORK
DATETIME_FORMAT = REST_FRAMEWORK['DATETIME_FORMAT']

from rest_auth.registration.serializers import RegisterSerializer

"""
! RULE : we do not serialize nested User, cuz User serializes user's role.
! RULE 2 : anymodel_set field inside other object should contain only url's to objects, not serialized objects
"""

"""
Internal stuff
"""
class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=100, required=False, allow_blank=True)


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


class CustomUserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email')
        read_only_fields = ('email',)

from rest_auth.registration.views import RegisterView

class CustomRegisterView(RegisterView):
    queryset = User.objects.all()

"""
MODELS Serializers
"""

class VoteSerializer(serializers.HyperlinkedModelSerializer):
    """ Returns serialized data of Vote instances. """
    class Meta:
        model = Vote
        fields = ('id', 'url', 'user', 'activity_type', 'date')

class UserSerializer(serializers.HyperlinkedModelSerializer):

    services_count = serializers.SerializerMethodField()
    def get_services_count(self, instance):
        return instance.services.count()

    posts_count = serializers.SerializerMethodField()
    def get_posts_count(self, instance):
        return instance.posts.count()

    income_reviews_count = serializers.SerializerMethodField()
    def get_income_reviews_count(self, instance):
        return instance.income_reviews.count()

    offers_count = serializers.SerializerMethodField()
    def get_offers_count(self, instance):
        return instance.offers.count()

    class Meta:
        model = User
        # TODO
        fields = ('id', 'url', 'email', 'phone', 'bio', 'first_name', 'last_name', 'image', \
                  #'services', 'posts', 'offers'
                  'services_count', 'posts_count', 'income_reviews_count', 'offers_count', \
                  'date_joined', \
                  )
        # outcome_reviews, income_reviwes
        read_only_fields = ('id', 'url', )

class PrivateUserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        # TODO
        fields = ('id', 'url', 'email', 'phone', 'bio', 'first_name', 'last_name',\
                  'service_promotions', 'post_promotions', 'services', 'posts', 'offers', \
                  'outcome_reviews', 'income_reviews')
        # outcome_reviews, income_reviwes
        read_only_fields = ('id', 'url', )

class DistrictSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'url', 'oblast', 'ekatte', 'name', 'region', )
        read_only_fields = ()
        lookup_field = 'oblast'
        extra_kwargs = {
            'url': {'lookup_field': 'oblast'}
        }

class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'url', 'ekatte', 't_v_m', 'name', 'oblast', 'obstina', 'kmetstvo', 'kind', 'category', 'altitude')
        read_only_fields = ()

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            # response['images'] = ServiceImageSerializer(instance.images, many=True, context = self.context).data
            # try:
            district = District.objects.get(oblast=instance.oblast)
            response['district'] = DistrictSerializer(district, many=False, context = self.context).data
            # except:
            #     pass
        return response




class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'url', 'name', 'color')
        read_only_fields = ('id', 'url',)
        required_fields = ('name',)
        extra_kwargs = {field: {'required': True} for field in required_fields}

class CategorySerializer(TagSerializer):
    class Meta(TagSerializer.Meta):
        model = Category

class ServiceImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ('id', 'url', 'service', 'image', )
        read_only_fields = ('id', 'url', )
        required_fields = ('service', 'image', )
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def get_image(self, data):
        request = self.context.get('request')
        imageurl = data.image.url
        return request.build_absolute_uri(imageurl)


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    images = ServiceImageSerializer(many=True, read_only=True)

    # likes = VoteSerializer(many=True, read_only=True)
    # dislikes = VoteSerializer(many=True, read_only=True)

    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='name'
    )

    category = serializers.SlugRelatedField(
        many=False,
        queryset=Category.objects.all(),
        slug_field='name'
    )

    current_user_vote = serializers.SerializerMethodField()
    def get_current_user_vote(self, instance):
        user = self.get_current_user()
        if not user:
            return None

        queryset = instance.votes.filter(user=user)
        if queryset.exists():
            vote = queryset.first()
            return VoteSerializer(vote, many=False, context=self.context).data
        return None

    class Meta:
        model = Service
        fields = ('id', 'url', 'author', 'title', 'description', 'price', 'price_currency', \
                  'contact_phone', 'contact_email', 'color', 'location', \
                  'images', 'promotions', 'is_promoted', \
                  'created_at', 'updated_at', 'tags', 'category', \
                  # 'likes', 'dislikes', \
                  'score', 'current_user_vote', 'price_details')
        read_only_fields = ('id', 'url', 'created_at', 'updated_at', 'author', 'images', 'promotions',\
                            # 'likes', 'dislikes', \
                            'score', 'current_user_vote')
        required_fields = ('title', 'description', 'price', 'price_currency', 'location')
        extra_kwargs = {field: {'required': True} for field in required_fields}


    def get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            return user
        return None

    def validate_author(self, value):
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError("Login please")

        user = request.user

        if user != value:
            raise serializers.ValidationError("You can not create services for another user")

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

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            # response['images'] = ServiceImageSerializer(instance.images, many=True, context = self.context).data
            response['author'] = UserSerializer(instance.author, many=False, context = self.context).data
            response['tags'] = TagSerializer(instance.tags, many=True, context = self.context).data
            response['category'] = CategorySerializer(instance.category, many=False, context = self.context).data
            response['location'] = LocationSerializer(instance.location, many=False, context = self.context).data
        return response

class ServicePromotionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServicePromotion
        fields = ('id', 'url', 'author', 'service', 'end_datetime', 'transaction_id', 'created_at', 'updated_at', 'is_valid', )
        read_only_fields = ('id', 'url', )
        required_fields = ('service', 'end_datetime', 'transaction_id', )
        extra_kwargs = {field: {'required': True} for field in required_fields}

## Post

class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'url', 'author', 'title', 'description', \
                  'contact_phone', 'contact_email', 'color', 'location', \
                  'images', 'promotions', 'offers', \
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'url', 'created_at', 'updated_at', 'author', 'images', 'promotions' )
        required_fields = ('title', 'description', )
        extra_kwargs = {field: {'required': True} for field in required_fields}


    def validate_author(self, value):
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError("Login please")

        user = request.user

        if user != value:
            raise serializers.ValidationError("You can not create posts for another user")

        return value

    def to_representation(self, instance):
        response = super().to_representation(instance)
        # if (self.context['request']):
        #     if getattr(instance, 'business', False):
        #         response['business'] = BusinessSerializer(instance.business, context = self.context).data
        return response

class PostImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PostImage
        fields = ('id', 'url', 'post', 'image')
        read_only_fields = ('id', 'url')
        required_fields = ('post', 'image')
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def get_image(self, data):
        request = self.context.get('request')
        imageurl = data.image.url
        return request.build_absolute_uri(imageurl)


class PostPromotionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PostPromotion
        fields = ('id', 'url', 'author', 'post', 'end_datetime', 'transaction_id', 'created_at', 'updated_at', 'is_valid')
        read_only_fields = ('id', 'url')
        required_fields = ('post', 'end_datetime', 'transaction_id')
        extra_kwargs = {field: {'required': True} for field in required_fields}



"""
url, title, text, created_at, updated_at
"""
class OfferSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'url', 'author', 'post', 'title', 'text', \
                  'price', 'color', 'is_public', \
                  'created_at', 'updated_at', 'answered', 'accepted')
        read_only_fields = ('id', 'url', 'author', 'created_at', 'updated_at')
        required_fields = ('post', 'title', 'text')
        extra_kwargs = {field: {'required': True} for field in required_fields}


    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            if getattr(instance, 'author', False):
                response['author'] = UserSerializer(instance.author, context = self.context).data
        return response


    def get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        if not user:
            raise serializers.ValidationError({"detail":"Login please"})
        return user

    def validate_on_answering(self):
        current_request = self.initial_data

        user = self.get_current_user()

        if current_request.answered:
            raise serializers.ValidationError({"detail": "Already answered"})
        elif current_request.author == user:
            raise serializers.ValidationError({"detail": "Only recipient can accept or reject request"})
        elif current_request.post.author != user:
            raise serializers.ValidationError({"detail": "Only recipient can accept or reject request"})
        return current_request


    def validate_author(self, value):
        user = self.get_current_user()

        if user.id != value.id:
            raise serializers.ValidationError("You must be author of request")
        return value


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'url', 'recipient', 'title', 'text', 'notification_datetime', 'notified', 'redirect_url')
        read_only_fields = ('id', 'url', 'notified')
        required_fields = ('recipient', 'title', 'text', 'notification_datetime')
        extra_kwargs = {field: {'required': True} for field in required_fields}

class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'url', 'author', 'recipient', 'service', 'title', 'text', 'grade', 'created_at', 'updated_at')
        read_only_fields = ('id', 'url', 'author')
        required_fields = ('service', 'title', 'grade')
        extra_kwargs = {field: {'required': True} for field in required_fields}


    def validate_recipient(self, value):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        if not user or value.id == user.id:
            raise serializers.ValidationError("You can not make reviews for yourself.")

        return value

