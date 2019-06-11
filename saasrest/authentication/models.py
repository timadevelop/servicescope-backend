from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils import timezone
from social_django.models import UserSocialAuth

import saasrest.local_settings

# Create your models here.


class UserManager(BaseUserManager):
    """
    User manager
    """
    use_in_migrations = True

    def create_user(self, email, password=None):
        """
        Custom create user method
        """
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Custom create staff user method
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Custom create super user method
        """
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
    """
    Main User model
    """
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
    last_active = models.DateTimeField(default=timezone.now)


    bio = models.TextField(max_length=500, blank=True, null=True)
    phone = models.TextField(max_length=100, blank=True, null=True)

    def upload_to(instance, filename):
        """
        Upload path string for user image
        """
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

    @property
    def is_verified_email(self):
        if self.is_staff:
            return True
        return EmailAddress.objects.filter(user=self, verified=True).exists()

    __original_email = None

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.__original_email = self.email

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.pk is not None and self.email != self.__original_email:
            email, email_created = EmailAddress.objects.get_or_create(
                user=self, email=self.__original_email)
            email.email = self.email
            email.primary = True
            email.verified = False
            email.save()
            request = HttpRequest()
            request.META['SERVER_NAME'] = saasrest.local_settings.API_HOST
            request.META['SERVER_PORT'] = saasrest.local_settings.API_PORT
            email.send_confirmation(request, signup=True)
        super(User, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_email = self.email



@receiver(post_save, sender=UserSocialAuth)
def on_user_created(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        email, email_created = EmailAddress.objects.get_or_create(
            user=user, email=user.email)
        if email_created:
            email.primary = True
            email.verified = False
            email.save()
            request = HttpRequest()
            request.META['SERVER_NAME'] = saasrest.local_settings.API_HOST
            request.META['SERVER_PORT'] = saasrest.local_settings.API_PORT
            email.send_confirmation(request, signup=True)
