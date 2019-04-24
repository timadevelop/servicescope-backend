from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.urls import reverse

from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from colorfield.fields import ColorField
from djmoney.models.fields import MoneyField


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

class Location(models.Model):
    LTYPE_CHOICES = (
        ('city', 'city'),
        ('vilage', 'vilage'),
        ('region', 'region'),
        ('area', 'area'),
    )

    ltype = models.CharField(
        max_length=10,
        blank=False,
        choices=LTYPE_CHOICES,
    )

    name = models.TextField(max_length=100, null=False, blank=False)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)


class Service(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')

    title = models.TextField(max_length=100, blank=False)
    description = models.TextField(max_length=900, blank=True)
    tags = models.ManyToManyField(Tag, related_name='services')
    category = models.ForeignKey(Category, related_name='services', null=True, blank=True, on_delete=models.SET_NULL)

    contact_phone = models.TextField(max_length=30, blank=True)
    contact_email = models.TextField(max_length=30, blank=True)

    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    color = ColorField(max_length=10, default='#686de0')

    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_promoted(self):
        return self.promotions.filter(end_datetime__gte=now()).exists()

class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=False, related_name='images')
    image = models.ImageField(upload_to='images/services/%Y/%m/%d')

class ServicePromotion(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_promotions')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions')

    end_datetime = models.DateTimeField(blank=False, null=False)
    transaction_id = models.CharField(max_length=110)

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


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_recipient')

    title = models.TextField(max_length=30)
    text = models.TextField(max_length=150)
    notification_datetime = models.DateTimeField(default=now, blank=False)
    notified = models.BooleanField(default=False)
    redirect_url = models.TextField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        # set notified to false on instance update
        if 'update_fields' not in kwargs or 'notified' not in kwargs['update_fields']:
            self.notified = False
        super(Notification, self).save(*args, **kwargs)

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
