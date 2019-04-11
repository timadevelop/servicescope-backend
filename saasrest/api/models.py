from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.urls import reverse

from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from colorfield.fields import ColorField


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
    # objects = UserManager()
    # EMAIL_FIELD = 'email'
    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']
    # def clean(self):
    #
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
    bio = models.TextField(max_length=500, blank=True)
    phone = models.TextField(max_length=100, blank=True)

    uid = models.TextField(max_length=22, blank=False, unique=True) # 22 due to google ids

    ROLE_CHOICES = (
        ('employee', 'employee'),
        ('customer', 'customer'),
        ('business', 'business'),
    )
    role = models.CharField(
        max_length=10,
        blank=False,
        choices=ROLE_CHOICES,
    )

    # stripe_id = models.CharField(max_length=250, blank=True)
    # plan = models.CharField(max_length=50)

    def __str__(self):              # __unicode__ on Python 2
        return 'User {} ({})'.format(self.first_name, self.email)


    # def get_absolute_url(self):
    #     return reverse('users', args=[str(self.id)])

    # returs user's role (business, )
    # @property
    # def role(self):
    #     employee = getattr(self, 'employee', False)
    #     customer = getattr(self, 'customer', False)
    #     business = getattr(self, 'business', False)
    #     if employee:
    #         return 'employee'
    #     elif customer:
    #         return 'customer'
    #     elif business:
    #         return 'business'
    #     else:
    #         return None

    # last_check_id = 
    @property
    def is_demo(self):
        return True
        # TODO
        # return self.date_joined < timezone.now() and self.is_active


"""
Receiver for user role creation
"""
@receiver(post_save, sender=User)
def create_user_role(sender, instance, created, **kwargs):
    if created:
        print('creating role {}'.format(instance.role))
        if instance.role == 'employee':
            Employee.objects.create(user=instance, uid=instance.uid)
        elif instance.role == 'business':
            Business.objects.create(user=instance, uid=instance.uid)
        elif instance.role == 'customer':
            Customer.objects.create(user=instance, first_name=instance.first_name, last_name=instance.last_name, uid=instance.uid)
        elif instance.role == 'admin':
            return None


"""
User roles
"""
class Business(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    location = models.CharField(max_length=50, blank=True)
    description = models.TextField(max_length=500, blank=True)
    color = ColorField(max_length=10, default='#3c6382')

    #inventory = models.ForeignKey(Inventory, null=True, on_delete=models.SET_NULL) #moved to related name
    uid = models.TextField(max_length=22, blank=False, unique=True) # 22 due to google ids

    # employee_set
    @property
    def title(self):
        return self.user.first_name

    def __str__(self):
        return 'Business of {}'.format(self.user)

"""
Inventory
"""


class Inventory(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='inventory')
    title = models.TextField(max_length=100, blank=False)
    # items as related name

    def __str__(self):
        return 'Inventory of {}'.format(self.business)

    # TODO: contains another inventory
    # def contains_inventory(self, inventory):
    #     for item in inventory.items:
    #

class InventoryItem(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='items')

    title = models.TextField(max_length=100, blank=False)
    # item uuid as barcode, not uuid for our db
    uuid = models.UUIDField(primary_key=False, editable=True)

    details = models.TextField(max_length=500, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    color = ColorField(max_length=10, default='#38ada9')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Inventory item {}'.format(self.title)

    @property
    def out_of_stock(self):
        return self.quantity == 0



class Employee(models.Model):
    #business = models.ForeignKey(Business, null=True, on_delete=models.SET_NULL)
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE)
    businesses = models.ManyToManyField(Business, blank=True)

    uid = models.TextField(max_length=22, blank=False, unique=True) # 22 due to google ids
    # rating = models.
    color = ColorField(max_length=10, default='#38ada9')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Employee {}".format(self.user)

    def add_business(self, business):
        if not self.businesses.filter(id=business.id).exists():
            self.businesses.add(business)
            self.save()

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name='customer')
    owner = models.ForeignKey(Business, null=True, on_delete=models.CASCADE)
    uid = models.TextField(max_length=22, blank=False, unique=True) # 22 due to google ids

    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    color = ColorField(max_length=10, default='#686de0')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Customer {}".format(self.user)

    def set_owner(self, business):
        if not self.owner == business:
            self.owner = business
            self.save()

"""
Main models
"""

"""
i.e. appeal to be customer of employee, employee of business, employee of customer
"""
class Appeal(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outcome_appeals')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='income_appeals')

    title = models.TextField(max_length=100, blank=False)
    text = models.TextField(max_length=500, blank=True)

    answered = models.BooleanField(default=False)
    accepted = models.NullBooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Service(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    title = models.TextField(max_length=30, blank=False)
    description = models.TextField(max_length=500, blank=True)
    price = models.TextField(max_length=30, blank=True)

    required_inventory = models.ForeignKey(Inventory, null=True, on_delete=models.SET_NULL, related_name='service')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # @property
    # def is_available(self):
    #     # TODO: is_available using business inventory check
    #     for item in self.required_inventory:
    #         if item not in self.business.inventory:
    #             return False
    #     return True

class Appointment(models.Model):
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL, related_name='appointment')
    service = models.ForeignKey(Service, null=True, on_delete=models.SET_NULL, related_name='appointment')

    employee = models.ForeignKey(Employee, null=True, on_delete=models.SET_NULL, related_name='appointment')
    business = models.ForeignKey(Business, null=True, on_delete=models.SET_NULL, related_name='appointment')
    # TODO: instead of business field use Share emplyee for each business

    title = models.TextField(max_length=30, blank=False, null=False)
    comment = models.TextField(max_length=200, blank=True, null=True)

    color = ColorField(max_length=10, default='#686de0')

    is_all_day = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    start_datetime = models.DateTimeField(default=now, blank=True)
    notification_datetime = models.DateTimeField(default=now, blank=True)
    end_datetime = models.DateTimeField(default=now, blank=True)

    notified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # set notified to false on instance update
        if 'update_fields' not in kwargs or 'notified' not in kwargs['update_fields']:
            self.notified = False
        super(Appointment, self).save(*args, **kwargs)


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
