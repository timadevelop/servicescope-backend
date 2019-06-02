from rest_framework import serializers
from .models import User, Notification, Review, \
    District, Location, Tag, Category, \
    Service, ServiceImage, ServicePromotion, \
    Post, PostImage, PostPromotion, Offer, Vote

from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, post_delete

from django.dispatch import receiver
import api.models as models

from django.urls import resolve

from django.db.models import Q

from datetime import datetime
from saasrest.settings import REST_FRAMEWORK
DATETIME_FORMAT = REST_FRAMEWORK['DATETIME_FORMAT']

from rest_auth.registration.serializers import RegisterSerializer

from .consumers import notify_user
from django.core.cache import cache

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

    def get_services_count(self, instance):
        return instance.services.count()

    def get_posts_count(self, instance):
        return instance.posts.count()

    def get_income_reviews_count(self, instance):
        return instance.income_reviews.count()

    def get_offers_count(self, instance):
        return instance.offers.count()

    def get_notifications_count(self, instance):
        return instance.notifications.filter(notified=False).count()

    class Meta:
        model = User
        # TODO
        fields = ('id', 'url', 'email', 'phone', 'bio', 'first_name', 'last_name', 'image', \
                  #'services', 'posts', 'offers'
                  'date_joined',)
        # outcome_reviews, income_reviwes
        read_only_fields = ('id', 'url', )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            if not isinstance(self.instance, list):
                  response['services_count'] = self.get_services_count(instance)
                  response['posts_count'] = self.get_posts_count(instance)
                  response['income_reviews_count'] = self.get_income_reviews_count(instance)
                  response['offers_count'] = self.get_offers_count(instance)
                  response['notifications_count'] = self.get_notifications_count(instance)

        return response

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
            district_data = cache.get('SERIALIZED_DISTRICT_{}'.format(instance.oblast))
            if district_data is None:
                district = District.objects.get(oblast=instance.oblast)
                district_data = DistrictSerializer(district, many=False, context = self.context).data
                cache.set('SERIALIZED_DISTRICT_{}'.format(instance.oblast), district_data)

            response['district'] = district_data
        return response




class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'color')
        read_only_fields = ()
        required_fields = ('name',)
        extra_kwargs = {field: {'required': True} for field in required_fields}

class CategorySerializer(TagSerializer):
    class Meta(TagSerializer.Meta):
        model = Category

class ServiceImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ('service', 'image', )
        read_only_fields = ()
        required_fields = ('service', 'image', )
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def get_image(self, data):
        request = self.context.get('request')
        imageurl = data.image.url
        return request.build_absolute_uri(imageurl)


from django.contrib.admin.options import get_content_type_for_model

class ServiceSerializer(serializers.HyperlinkedModelSerializer):
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
            user_instances_votes = self.context.get('user_instances_votes', None)
            if user_instances_votes is None:
                ct = get_content_type_for_model(instance)
                l = list(user.votes.filter(content_type=ct, object_id__in=[i.pk for i in self.instance]))
                self.context["user_instances_votes"] = { v.object_id: v for v in l}
                user_instances_votes = self.context["user_instances_votes"]

            vote = user_instances_votes.get(instance.id, None)
            if vote:
                return VoteSerializer(vote, many=False, context=self.context).data

        return None

    class Meta:
        model = Service
        fields = ('id', 'url', 'author', 'title', 'description', 'price', 'price_currency', \
                  'contact_phone', 'contact_email', 'color', 'location', \
                  'images', \
                  'promoted_til',
                  'is_promoted', \
                  'created_at', 'updated_at', \
                  'tags', 'category', \
                  # 'promotions', \
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
            return request.user
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
            if not isinstance(self.instance, list):
                response['author'] = UserSerializer(instance.author, many=False, context = self.context).data

            # response['images'] = ServiceImageSerializer(instance.images, many=True, context = self.context).data
            # response['category'] = CategorySerializer(instance.category, many=False, context = self.context).data

            response['tags'] = TagSerializer(instance.tags, many=True, context = self.context).data
            response['location'] = cached_or_new('SERIALIZED_LOCATION_{}'.format(instance.id), LocationSerializer, instance, 'location', self.context)
            #response['location'] = LocationSerializer(instance.location, many=False, context = self.context).data
        return response

def cached_or_new(key, serializer_class, instance, object_property_name, context, many=False):
    result = cache.get(key)
    if result is None:
        obj = getattr(instance, object_property_name, False)
        result = serializer_class(obj, many=many, context = context).data
        cache.set(key, result)

    return result

class ShortServiceSerializer(ServiceSerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            response['tags'] = TagSerializer(instance.tags, many=True, context = self.context).data
            response['location'] = cached_or_new('SERIALIZED_LOCATION_{}'.format(instance.id), LocationSerializer, instance, 'location', self.context)
        return response

class ServicePromotionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServicePromotion
        fields = ('id', 'url', 'author', 'service', 'end_datetime', 'stripe_payment_intents', 'transaction_id', 'created_at', 'updated_at', 'is_valid', )
        read_only_fields = ('id', 'url', )
        required_fields = ('service', 'end_datetime', 'transaction_id', )
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            # response['author'] = UserSerializer(instance.author, many=False, context = self.context).data
            response['service'] = ShortServiceSerializer(instance.service, many=False, context = self.context).data
        return response

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

        if not user or user.is_anonymous:
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



@receiver(post_save, sender=models.Notification, dispatch_uid='notification_post_save_signal')
def send_new_notification(sender, instance, created, **kwargs):
    def send_notification(notification):
        if not notification or not getattr(notification, 'recipient', False):
            return False
        serializer = NotificationSerializer(notification, many=False, context = {'request': None})
        async_to_sync(notify_user)(notification.recipient.id, serializer.data)

    if created:
        send_notification(instance)

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

        if not user or user.is_anonymous or value.id == user.id:
            raise serializers.ValidationError("You can not make reviews for yourself.")

        return value



class ConversationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Conversation
        fields = ('id', 'url', 'title', 'users', 'created_at', 'updated_at')
        required_fields = ('users', 'title')
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def to_representation(self, instance):
        response = super().to_representation(instance)
        user = self.get_current_user()
        if (self.context['request']) and user:
            users = instance.users.exclude(id=user.id)
            response['users'] = UserSerializer(users, many=True, context = self.context).data
        return response

    def get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            return user
        return None

    def validate_users(self, value):
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError("Login please")

        user = request.user

        if len(value) != 2:
            raise serializers.ValidationError("2 Users required")

        users = value
        request_user_is_in_users = False
        for u in users:
            if u.id == user.id:
                request_user_is_in_users = True

        if not request_user_is_in_users:
            raise serializers.ValidationError("Users field must contain request user")

        q = models.Conversation.objects.all()
        for u in users:
            q = q.filter(users=u)

        if q.exists():
            raise serializers.ValidationError("Conversation exists")


        return value

    def get_obj_from_url(self, url):
        return resolve(url).func.cls.serializer_class.Meta.model.objects.get(**resolve(url).kwargs)

class MessageImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.MessageImage
        fields = ('id', 'url', 'message', 'image', )
        read_only_fields = ('id', 'url', )
        required_fields = ('message', 'image', )
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def get_image(self, data):
        request = self.context.get('request')
        imageurl = data.image.url
        return request.build_absolute_uri(imageurl)


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    is_my_message = serializers.SerializerMethodField()
    images = MessageImageSerializer(many=True, read_only=True)

    class Meta:
        model = models.Message
        fields = ('id', 'url', 'author', 'conversation', 'text', 'created_at', 'updated_at', 'is_my_message', 'images')
        required_fields = ('conversation', 'text', )
        extra_kwargs = {field: {'required': True} for field in required_fields}
        read_only_fields = ('id', 'url', 'author', 'created_at', 'updated_at', 'is_my_message')

    def validate_conversation(self, value):
        user = self.get_current_user()

        is_in_conversation = value.users.all().filter(id=user.id).exists()
        if not is_in_conversation:
            raise serializers.ValidationError("You're not in conversation")

        return value

    def validate_author(self, value):
        user = self.get_current_user()
        if user.id != value.id:
            raise serializers.ValidationError("Request user must be author")

        return value

    def create(self, validated_data):
        message = super().create(validated_data)
        image_data = self.context.get('view').request.FILES
        for img in image_data.values():
            img = models.MessageImage.objects.create(message=message, image=img)
        return message

    def update(self, instance, validated_data):
        message = super().update(instance, validated_data)
        image_data = self.context.get('view').request.FILES
        for img in image_data.values():
            img = models.MessageImage.objects.create(message=message, image=img)
        return message

    def get_is_my_message(self, instance):
        user = self.get_current_user()
        if not user:
            return False

        return instance.author.id == user.id

    def get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            return user
        return None

    def to_representation(self, instance):
        response = super().to_representation(instance)
        # if (self.context['request']):
        #     if not self.get_is_my_message(instance):
        #         response['author'] = UserSerializer(instance.author, many=False, context = self.context).data
        # else:
        # response['author'] = UserSerializer(instance.author, many=False, context = self.context).data
        return response

    def group_name(self, instance):
        return instance.conversation.id


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    recipient_id = serializers.SerializerMethodField()
    def get_recipient_id(self, instance):
        recipient = getattr(instance, 'recipient', None)
        if recipient:
            return recipient.id
        else:
            return None

    conversation_id = serializers.SerializerMethodField()
    def get_conversation_id(self, instance):
        conversation = getattr(instance, 'conversation', None)
        if conversation:
            return conversation.id
        else:
            return None

    class Meta:
        model = Notification
        fields = ('id', 'url', 'recipient', 'conversation', 'conversation_id', 'recipient_id', 'title', 'type', 'text', 'notification_datetime', 'notified', 'redirect_url', 'created_at', 'updated_at')
        read_only_fields = ('id', 'url', 'notified')
        required_fields = ('recipient', 'title', 'text', 'notification_datetime')
        extra_kwargs = {field: {'required': True} for field in required_fields}

    # def create(self, validated_data):
    #     obj = models.Notification.objects.create(**validated_data)
    #     return obj
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     if (self.context['request']) and getattr(instance, 'conversation', False):
    #         response['conversation'] = ConversationSerializer(instance.conversation, many=False, context = self.context).data
    #     return response


class FeedbackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Feedback
        fields = ('id', 'url', 'author', 'rate', 'text', 'created_at')
        read_only_fields = ('id', 'url', 'author', 'created_at')
        required_fields = ('rate', 'text')
        extra_kwargs = {field: {'required': True} for field in required_fields}

