from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

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
