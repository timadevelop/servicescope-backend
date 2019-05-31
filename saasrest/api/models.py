from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.urls import reverse

from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from colorfield.fields import ColorField
from djmoney.models.fields import MoneyField
from django.contrib.postgres.fields import JSONField

from django.contrib.contenttypes.models import ContentType

from django.contrib.postgres.fields import ArrayField

from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
# except ImportError:
#     from django.contrib.contenttypes.generic import GenericForeignKey

# class VoteManager(models.Manager):
#     def filter(self, *args, **kwargs):
#         if 'content_object' in kwargs:
#             content_object = kwargs.pop('content_object')
#             content_type = ContentType.objects.get_for_model(content_object)
#             kwargs.update({
#                 'content_type': content_type,
#                 'object_id': content_object.pk
#             })
#         return super(VoteManager, self).filter(*args, **kwargs)
#
#
# class Vote(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey()
#     create_at = models.DateTimeField(auto_now_add=True)
#
#     vote = models.NullBooleanField()
#     objects = VoteManager()
#
#     class Meta:
#         unique_together = ('user', 'content_type', 'object_id')
#
#     @classmethod
#     def votes_for(cls, model, instance=None):
#
#         ct = ContentType.objects.get_for_model(model)
#         kwargs = {
#             "content_type": ct
#         }
#         if instance is not None:
#             kwargs["object_id"] = instance.pk
#
#         return cls.objects.filter(**kwargs)
#
class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password=None):
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    # username = models.CharField(
    # first_name = models.CharField(_('first name'), max_length=30, blank=True)
    # last_name = models.CharField(_('last name'), max_length=150, blank=True)
    # email = models.EmailField(_('email address'), blank=True)
    # is_staff = models.BooleanField(
    #     help_text=_('Designates whether the user can log into this admin site.'),
    # is_active = models.BooleanField(
    #         'Designates whether this user should be treated as active. '
    #         'Unselect this instead of deleting accounts.'
    # is_admin ?
    # date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    # def clean(self):
    # def get_full_name(self):
    #     Return the first_name plus the last_name, with a space in between.
    # def get_short_name(self):
    #     """Return the short name for the user."""
    # def email_user(self, subject, message, from_email=None, **kwargs):
    #     """Send an email to this user."""

    # auth fields
    username = None
    email = models.EmailField(('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    # additional fields
    online = models.PositiveIntegerField(default=0)

    bio = models.TextField(max_length=500, blank=True, null=True)
    phone = models.TextField(max_length=100, blank=True, null=True)

    def upload_to(instance, filename):
        return 'images/users/%s/%s' % (instance.id, filename)

    image = models.ImageField(upload_to=upload_to, blank=True)

    # stripe_id = models.CharField(max_length=250, blank=True)
    # plan = models.CharField(max_length=50)

    def __str__(self):              # __unicode__ on Python 2
        return 'User {} ({})'.format(self.first_name, self.email)


    # def get_absolute_url(self):
    #     return reverse('users', args=[str(self.id)])

    @property
    def is_demo(self):
        return True
        # TODO
        # return self.date_joined < timezone.now() and self.is_active

"""
Receiver for user payments?
# TODO:
"""
# @receiver(post_save, sender=User)
# def create_user_role(sender, instance, created, **kwargs):
#     if created:
#         print('creating role {}'.format(instance.role))
#         if instance.role == 'employee':
#             Employee.objects.create(user=instance, uid=instance.uid)
#         elif instance.role == 'business':
#             Business.objects.create(user=instance, uid=instance.uid)
#         elif instance.role == 'customer':
#             Customer.objects.create(user=instance, first_name=instance.first_name, last_name=instance.last_name, uid=instance.uid)
#         elif instance.role == 'admin':
#             return None
#
class Vote(models.Model):
    FAVORITE = 'F'
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    ACTIVITY_TYPES = (
        (FAVORITE, 'Favorite'),
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)
    date = models.DateTimeField(auto_now_add=True)

    # Below the mandatory fields for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()



@receiver(post_save, sender=Vote, dispatch_uid='vote_post_save_signal')
def update_obj_score(sender, instance, created, **kwargs):
    if created:
        obj = instance.content_object
        obj.score = obj.likes.count() - obj.dislikes.count()
        obj.save(update_fields=['score'])


@receiver(post_delete, sender=Vote, dispatch_uid='vote_pre_delete_signal')
def change_obj_score(sender, instance, using, **kwargs):
    obj = instance.content_object
    obj.score = obj.likes.count() - obj.dislikes.count()
    obj.save(update_fields=['score'])



class Tag(models.Model):
    name = models.TextField(max_length=20, blank=False, null=False, unique=True)
    color = ColorField(max_length=10, default='#686de0')

    def __str__(self):
        return 'Tag[id: {id}, name: {name}]'.format(id=self.id, name=self.name)


class Category(models.Model):
    name = models.TextField(max_length=20, blank=False, null=False, unique=True)
    color = ColorField(max_length=10, default='#686de0')

    def __str__(self):
        return 'Category[id: {id}, name: {name}]'.format(id=self.id, name=self.name)

class District(models.Model):
    oblast = models.TextField(max_length=5, blank=False, null=False)
    ekatte = models.TextField(max_length=5, blank=False, null=False)

    name = models.TextField(max_length=100, null=False, blank=False)
    region = models.TextField(max_length=5, blank=False, null=False)


class Location(models.Model):
    ekatte = models.TextField(max_length=5, blank=False, null=False)
    t_v_m = models.TextField(max_length=5, blank=False, null=False)
    name = models.TextField(max_length=100, null=False, blank=False)
    oblast = models.TextField(max_length=5, blank=False, null=False)
    obstina = models.TextField(max_length=5, blank=False, null=False)
    kmetstvo= models.TextField(max_length=10, blank=False, null=False)

    kind = models.PositiveSmallIntegerField(blank=False, null=False)
    category = models.PositiveSmallIntegerField(blank=False, null=False)
    altitude = models.PositiveSmallIntegerField(blank=False, null=False)


class Service(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')

    title = models.TextField(max_length=100, blank=False)
    description = models.TextField(max_length=900, blank=True)
    tags = models.ManyToManyField(Tag, related_name='services')
    category = models.ForeignKey(Category, related_name='services', null=True, blank=True, on_delete=models.SET_NULL)

    contact_phone = models.TextField(max_length=30, blank=True)
    contact_email = models.TextField(max_length=30, blank=True)

    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    price_details = JSONField(default=list)

    color = ColorField(max_length=10, default='#686de0')

    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    score = models.IntegerField(default=0)
    votes = GenericRelation(Vote)
    promoted_til = models.DateTimeField(null=True, blank=True)
    # @property
    # def likes(self):
    #     return self.votes.filter(activity_type=Vote.UP_VOTE)
    #
    # @property
    # def dislikes(self):
    #     return self.votes.filter(activity_type=Vote.DOWN_VOTE)

    # hints
    # Get the post object
    #post = Post.objects.get(pk=1)
    # Add a like activity
    #post.likes.create(activity_type=Vote.LIKE, user=request.user)
    # Or in a similar way using the Activity model to add the like
    #Vote.objects.create(content_object=post, activity_type=Activity.LIKE, user=request.user)

    @property
    def is_promoted(self):
        if self.promoted_til and self.promoted_til < now():
            return True
        return False

class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=False, related_name='images')
    image = models.ImageField(upload_to='images/services/%Y/%m/%d')

class ServicePromotion(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_promotions')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions')

    end_datetime = models.DateTimeField(blank=False, null=False)
    transaction_id = models.CharField(max_length=110)

    stripe_payment_intents = ArrayField(models.CharField(max_length=110))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def is_valid(self):
        return self.end_datetime > now()

"""
i.e. post to be customer of employee, employee of business, employee of customer
"""
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    title = models.TextField(max_length=100, blank=False)
    description = models.TextField(max_length=500, blank=True)

    contact_phone = models.TextField(max_length=30, blank=True)
    contact_email = models.TextField(max_length=30, blank=True)

    color = ColorField(max_length=10, default='#686de0')

    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False, related_name='images')
    image = models.ImageField(upload_to='images/posts/%Y/%m/%d')

class PostPromotion(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='post_promotions')
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions')

    end_datetime = models.DateTimeField(default=now, blank=True)
    transaction_id = models.CharField(max_length=110)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def is_valid(self):
        return self.end_datetime > now()


class Offer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='offers')

    title = models.TextField(max_length=30, blank=False, null=False)
    text = models.TextField(max_length=200, blank=True, null=True)

    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    color = ColorField(max_length=10, default='#686de0')

    is_public = models.BooleanField(default=True)

    answered = models.BooleanField(default=False)
    accepted = models.NullBooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Review(models.Model):
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='outcome_reviews')
    recipient = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='income_reviews')
    # and
    service = models.ForeignKey(Service, null=True, on_delete=models.SET_NULL)

    title = models.TextField(max_length=100, blank=False)
    text = models.TextField(max_length=1000, blank=True)
    grade= models.TextField(max_length=10, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Conversation(models.Model):
    title = models.TextField(max_length=30, blank=False)
    # related messages field
    # TODO: rm from users current user on response
    users = models.ManyToManyField(User, related_name="conversations")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='messages')
    conversation = models.ForeignKey(Conversation, null=False, on_delete=models.CASCADE, related_name='messages')

    text = models.TextField(max_length=1000, blank=True)
    # related images field

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MessageImage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=False, related_name='images')
    image = models.ImageField(upload_to='images/messages/%Y/%m/%d')

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)

    title = models.TextField(max_length=30)
    text = models.TextField(max_length=150)
    notification_datetime = models.DateTimeField(default=now, blank=False)
    notified = models.BooleanField(default=False)
    redirect_url = models.TextField(max_length=20, blank=True)
    type = models.TextField(max_length=30, default="info")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # set notified to false on instance update
        if 'update_fields' not in kwargs or 'notified' not in kwargs['update_fields']:
            self.notified = False
        super(Notification, self).save(*args, **kwargs)



class Feedback(models.Model):
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='feedbacks')
    text = models.TextField(max_length=2000, blank=True)
    rate = models.DecimalField(max_digits=2, decimal_places=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

