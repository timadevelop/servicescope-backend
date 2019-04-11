from rest_framework import serializers
from .models import User, Business, Employee, Customer, \
    Appointment, Appeal, Notification, Review, \
    Service, \
    InventoryItem, Inventory

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
    uid = serializers.CharField(required=True, max_length=22)
    role = serializers.ChoiceField(required=True, choices=User.ROLE_CHOICES)
    bio = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)

    def validate_uid(self, value):
        if User.objects.filter(uid=value).exists():
            raise serializers.ValidationError("There is already user with uid '{}'".format(value))

        return value

    def get_cleaned_data(self):
        super(CustomRegisterSerializer, self).get_cleaned_data()

        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'role': self.validated_data.get('role', 'null'),
            'phone': self.validated_data.get('phone', ''),
            'bio': self.validated_data.get('bio', ''),
            'uid': self.validated_data.get('uid', ''),
        }
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            phone=validated_data['phone'],
            uid=validated_data['uid'],
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
"""
url, location, bio, role (customer, employee, or business as string)

user: UserSerializer
employee: EmployeeSerializer
customer: CustomerSerializer
business: BusinessSerializer
"""
class UserSerializer(serializers.HyperlinkedModelSerializer):
    new_appeals_count = serializers.SerializerMethodField()

    def get_new_appeals_count(self, instance):
        # user = self.get_current_user()
        # if user:
        #     queryset = Appeal.objects.filter(recipient=user, answered=False)
        #     return queryset.count()
        return 0

    class Meta:
        model = User
        fields = ('url', 'email', 'phone', 'bio', 'business', 'employee', 'customer','role', 'new_appeals_count', 'first_name', 'last_name', 'income_appeals', 'outcome_appeals')
        # outcome_reviews, income_reviwes
        read_only_fields = ('business', 'employee', 'customer', 'role')


    def get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        return user
    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            employee = getattr(instance, 'employee', False)
            business = getattr(instance, 'business', False)
            customer = getattr(instance, 'customer', False)
            if employee:
                response['employee'] = EmployeeSerializer(instance.employee, context = self.context).data
            if business:
                response['business'] = BusinessSerializer(instance.business, context = self.context).data
            if customer:
                response['customer'] = CustomerSerializer(instance.customer, context = self.context).data
        return response


"""
Inventory serializers
"""

class InventorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Inventory
        fields = ('url', 'items', 'business', 'title')
        read_only_fields = ('url', 'items', 'business')
        required_fields = ('title')
        extra_kwargs = {field: {'required': True} for field in required_fields}


    def get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        return user

    def validate_business(self, value):
        user = self.get_current_user()

        if user.id != value.user.id:
            raise serializers.ValidationError("You can create inventory for your business only")

        return value

class InventoryItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ('url', 'inventory', 'title', 'uuid', 'details', 'quantity', 'color', 'updated_at', 'created_at')
        read_only_fields = ('url', 'updated_at', 'created_at', )
        required_fields = ('title', 'uuid', 'inventory')
        extra_kwargs = {field: {'required': True} for field in required_fields}


    def get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        return user

    def validate_inventory(self, value):
        user = self.get_current_user()

        if user.id != value.business.user.id:
            raise serializers.ValidationError("You can add items only to your inventory")

        return value
"""
User roles
"""
#url, title, user (URL, NOT obj), uid, color, is_my_business, employee_set (set of urls to /employees/)
class BusinessSerializer(serializers.HyperlinkedModelSerializer):
    is_my_business = serializers.SerializerMethodField()

    def get_is_my_business(self, instance):
        user = self.get_current_user()
        if user and user.role == 'employee' and \
                getattr(user.employee, 'business', False) and \
                user.employee.business.id == instance.id:
                return True
        elif user and user.role == 'business':
            return instance.id == user.business.id
        return False

    def get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        return user

    class Meta:
        model = Business
        fields = ('url', 'title', 'user', 'location', 'description', 'inventory', 'color', 'employee_set', 'is_my_business', 'uid')
        read_only_fields = ('url', 'user', 'employee_set')

    def validate_user(self, value):
        if hasattr(value, 'business') and value.business:
            raise serializers.ValidationError({"detail":"This user is already taken by another business"})
        if hasattr(value, 'employee') and value.employee:
            raise serializers.ValidationError({"detail":"This user already belongs to a employee"})
        return value


"""
url, user (URL, NOT obj), first_name, last_name, uid, is_my_employee: bool

business: BusinessSerializer (object)
customer_set: set of urls to /customers/
"""
class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    is_my_employee = serializers.SerializerMethodField()

    def get_is_my_employee(self, instance):
        user = self.get_current_user()
        if user and user.role == 'business':
            employees = user.business.employee_set
            if employees.filter(id=instance.id).exists():
                return True
        return False

    def get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        return user

    class Meta:
        model = Employee
        fields = ('url', 'user', 'businesses', 'created_at', 'updated_at' , 'color', 'is_my_employee', 'uid')
        read_only_fields = ('url', 'user', 'created_at', 'updated_at')

    def validate_user(self, value):
        if hasattr(value, 'business') and value.business:
            raise serializers.ValidationError({"detail":"This user is taken by business"})
        if hasattr(value, 'employee') and value.employee:
            raise serializers.ValidationError({"detail":"This user alreary belongs to a employee"})
        if hasattr(value, 'customer') and value.customer:
            raise serializers.ValidationError({"detail":"This user alreary belongs to a employee"})
        return value

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            if getattr(instance, 'business', False):
                response['business'] = BusinessSerializer(instance.business, context = self.context).data
        return response


"""
url, first_name, last_name, uid, color: hex, is_my_customer: bool

employee: EmployeeSerializer object
"""
class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    is_my_customer = serializers.SerializerMethodField()

    def get_is_my_customer(self, instance):
        user = self.get_current_user()
        if user and user.role == 'business':
            return user.business == instance.owner
        return False

    class Meta:
        model = Customer
        fields = ('url', 'user', 'owner',  'first_name', 'last_name', 'is_my_customer', 'color', 'uid')
        read_only_fields = ('url', 'user')
        required_fields = ('user', )
        extra_kwargs = {field: {'required': True} for field in required_fields}

    def validate_user(self, value):
        if hasattr(value, 'business') and value.business:
            raise serializers.ValidationError({"detail":"This user is taken by business"})
        if hasattr(value, 'employee') and value.employee:
            raise serializers.ValidationError({"detail":"This user alreary belongs to a employee"})
        if getattr(value, 'customer', False):
            raise serializers.ValidationError({"detail":"This user alreary belongs to a employee"})
        return value

    def get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        return user

    def to_representation(self, instance):
        response = super().to_representation(instance)
        return response


"""
Other models serialziers
"""

"""
url, data (just a text), is_public: bolean

employee: EmployeeSerializer object
customer: CustomerSerializer object
"""
class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('url', 'business', 'title', 'description', 'price', 'required_inventory', 'created_at', 'updated_at', 'review_set')
        read_only_fields = ('url', 'created_at', 'updated_at', 'business' )
        required_fields = ('title', 'price')
        extra_kwargs = {field: {'required': True} for field in required_fields}


    def validate_title(self, value):
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError("Login please")

        user = request.user

        if user.role != 'business':
            raise serializers.ValidationError("Login as business please")

        if Service.objects.filter(business=user.business).filter(title=value).exists():
            raise serializers.ValidationError("There is already an service with title {} in your business".format(value))

        return value

    def to_representation(self, instance):
        response = super().to_representation(instance)
        # if (self.context['request']):
        #     if getattr(instance, 'business', False):
        #         response['business'] = BusinessSerializer(instance.business, context = self.context).data
        return response


    # def validate_employee(self, value):
    #     user = None
    #     request = self.context.get("request")
    #     if request and hasattr(request, "user"):
    #         user = request.user
    #         if user.role == 'customer':
    #             employees = user.customer.employees
    #             valid_employee = employees.filter(id=value.id).exists()
    #             if not valid_employee:
    #                 raise serializers.ValidationError({"detail":"This employee is not yours"})
    #         elif user.role != 'employee' or user.employee != value:
    #             raise serializers.ValidationError({"detail":"You cannot create data for other employee"})
    #     return value
    #
    # def validate_customer(self, value):
    #     user = None
    #     request = self.context.get("request")
    #     if request and hasattr(request, "user"):
    #         user = request.user
    #
    #     if not hasattr(user, 'user'):
    #         raise serializers.ValidationError({"detail":"Your user has no user, write admins"})
    #
    #     role = getattr(user, 'role', False)
    #
    #     if role != 'employee' and role != 'customer':
    #         raise serializers.ValidationError({"detail":"You're not employee or customer"})
    #
    #     if role == 'employee' and not value.employees.filter(id=user.employee.id).exists():
    #         raise serializers.ValidationError({"detail":"This customer is not yours"})
    #
    #     if role == 'customer' and user.customer != value:
    #         raise serializers.ValidationError({"detail":"As customer you can create Data only for yourself."})
    #
    #     return value

"""
employee: EmployeeSerializer object
redirect_employee: EmployeeSerializer object
customer: CustomerSerializer object
"""
# class RecipeSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Recipe
#         fields = ('url', 'customer', 'employee', 'redirect_employee', 'is_public', 'diagnosis', 'drugs', 'created_at', 'updated_at')
#         read_only_fields = ('url', 'employee', 'created_at', 'updated_at')
#         required_fields = ('customer', 'diagnosis', 'drugs')
#         extra_kwargs = {field: {'required': True} for field in required_fields}
#
#
#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         if (self.context['request']):
#             if getattr(instance, 'employee', False):
#                 response['employee'] = EmployeeSerializer(instance.employee, context = self.context).data
#             if getattr(instance, 'redirect_employee', False):
#                 response['redirect_employee'] = EmployeeSerializer(instance.redirect_employee, context = self.context).data
#             if getattr(instance, 'customer', False):
#                 response['customer'] = CustomerSerializer(instance.customer, context = self.context).data
#         return response
#     # def get_image(self, data):
#     #     request = self.context.get('request')
#     #     imageurl = data.image.url
#     #     return request.build_absolute_uri(imageurl)
#     def validate_employee(self, value):
#         user = None
#         request = self.context.get("request")
#         if request and hasattr(request, "user"):
#             user = request.user
#
#         if not hasattr(user, 'employee') or user.employee != value:
#             raise serializers.ValidationError({"detail":"You cannot create recipe for other employee"})
#         return value
#
#     def validate_redirect_employee(self, value):
#         user = None
#         request = self.context.get("request")
#         if request and hasattr(request, "user"):
#             user = request.user
#
#         if not hasattr(user, 'employee') or user.employee == value:
#             raise serializers.ValidationError({"detail":"You cannot redirect recipe to yourself"})
#         return value
#
#     def validate_customer(self, value):
#         user = None
#         request = self.context.get("request")
#         if request and hasattr(request, "user"):
#             user = request.user
#
#         if not hasattr(user, 'user'):
#             raise serializers.ValidationError({"detail":"Your user has no user, write admins"})
#
#
#     def validate_customer(self, value):
#         user = None
#         request = self.context.get("request")
#         if request and hasattr(request, "user"):
#             user = request.user
#
#         if not hasattr(user, 'user'):
#             raise serializers.ValidationError({"detail":"Your user has no user, write admins"})
#
#         if not hasattr(user, 'employee'):
#             raise serializers.ValidationError({"detail":"You're not employee"})
#
#         if not value.employees.filter(id=user.employee.id).exists():
#             raise serializers.ValidationError({"detail":"This customer is not yours"})
#         return value





"""
url, title, text, created_at, updated_at

author: UserSerializer object
recipient: UserSerializer object
"""
class AppealSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Appeal
        fields = ('url', 'author', 'recipient', 'title', 'text', 'created_at', 'updated_at', 'answered', 'accepted')
        read_only_fields = ('url', 'author', 'created_at', 'updated_at')
        required_fields = ('recipient', 'title', 'text')
        extra_kwargs = {field: {'required': True} for field in required_fields}


    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            if getattr(instance, 'author', False):
                response['author'] = UserSerializer(instance.author, context = self.context).data
            if getattr(instance, 'recipient', False):
                response['recipient'] = UserSerializer(instance.recipient, context = self.context).data
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
        elif current_request.recipient != user:
            raise serializers.ValidationError({"detail": "Only recipient can accept or reject request"})
        return current_request

    def validate_on_accepting(self, author=None, recipient=None):
        if not author or not recipient:
            current_request = self.initial_data

            author = current_request.author
            recipient = current_request.recipient

        if author.role == 'employee':
            # from employee
            # if recipient.role == 'customer':
            #     return True
            if recipient.role == 'business':
                # to business (author asks to be registered in business, business accepted)
                employee = author.employee
                if employee.businesses.filter(id=recipient.business.id).exists():
                    raise serializers.ValidationError({"detail": "Employee is already in business"})
                return True
            else:
                raise serializers.ValidationError({"detail": "Employee can send requests only to business"})
        elif author.role == 'customer':
            # from customer
            # if recipient.role == 'employee':
            #     # to employee (ask employee if he wants author to be his customer, employee can accept/reject)
            #     return True
            # if recipient.role == 'business':
            #     # to employee (ask employee if he wants author to be his customer, employee can accept/reject)
            #     return True
            # else:
            raise serializers.ValidationError({"detail": "Customer can not send requests"})
        elif author.role == 'business':
            # from business
            if recipient.role == 'employee':
                # to employee (ask employee if he wants to be in business)
                employee = recipient.employee
                if employee.businesses.filter(id=author.business.id).exists():
                    print('herfe')
                    raise serializers.ValidationError({"detail": "Employee is already in business"})
                return True
            # elif recipient.role == 'customer':
            #     return True
            else:
                raise serializers.ValidationError({"detail": "Business can send requests only to employees"})
        else:
            raise serializers.ValidationError({"detail": "Author role is wrong"})


    def validate_author(self, value):
        user = self.get_current_user()

        if user.id != value.id:
            raise serializers.ValidationError({"detail":"You must be author of request"})
        return value

    def validate_recipient(self, value):
        user = self.get_current_user()
        author = user
        recipient = value

        if user.id == recipient.id:
            raise serializers.ValidationError({"detail":"You cannot make requests to yourself"})

        if not recipient or not getattr(recipient, 'role', False):
            raise serializers.ValidationError({"detail":"Bad recipient"})
        if author.role == 'employee':
            if recipient.role != 'customer' and recipient.role != 'business':
                raise serializers.ValidationError({"detail":"Employee can send requests only to customer or business"})
        elif author.role == 'customer':
            if recipient.role == 'customer':
                raise serializers.ValidationError({"detail":"Customer can not send requests to customers"})
        elif author.role == 'business':
            if recipient.role == 'business':
                raise serializers.ValidationError({"detail":"Business can not send appeals to businesses"})
        else:
            raise serializers.ValidationError({"detail":"Author role is wrong"})

        self.validate_on_accepting(author, recipient)


        return value



"""
for datetime see FORMAT in saasrest.settings.py

url, title, is_public, start_datetime:formated date string, notification_datetime, end_datetime
color: hex color, category: string, is_all_day: boolean

customer: CustomerSerializer object
employee: EmployeeSerializer object
"""
class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    # customer = CustomerSerializer(many=False)
    # employee = EmployeeSerializer(many=False)
    class Meta:
        model = Appointment
        fields = ('url', 'customer',  'business', 'employee', 'title', 'comment', 'start_datetime', 'notification_datetime', 'end_datetime', 'color', 'is_public', 'is_all_day', 'notified')
        read_only_fields = ('url', 'customer', 'notified', )
        required_fields = ('customer', 'title', 'start_datetime', 'end_datetime', 'business')
        extra_kwargs = {field: {'required': True} for field in required_fields}


    def to_representation(self, instance):
        response = super().to_representation(instance)
        if (self.context['request']):
            if getattr(instance, 'employee', False):
                response['employee'] = EmployeeSerializer(instance.employee, context = self.context).data
            if getattr(instance, 'customer', False):
                response['customer'] = CustomerSerializer(instance.customer, context = self.context).data
        return response

    def validate_notification_datetime(self, value):
        request = self.context.get("request")
        if request and not value and 'start_datetime' in request.data:
            # set start_datetime as notification datetime
            # print('set start_datetime')
            return request.data.get('start_datetime')
        else:
            return value

    def validate_employee(self, value):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        if hasattr(user, 'employee') and user.employee != value:
            raise serializers.ValidationError("You cannot create data for other employee")
        elif hasattr(user, 'business') and not value.businesses.filter(id=user.business.id).exists():
            raise serializers.ValidationError("Employee is not from your business")

        return value

    def validate_business(self, value):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        role = getattr(user, 'role', False)

        if role == 'employee' and not value.employee_set.filter(id=user.employee.id).exists():
            raise serializers.ValidationError("This business is not yours")

        if role == 'business' and user.business != value:
            raise serializers.ValidationError("As business you can create Appointments only for yourself.")

        return value


    def validate_customer(self, value):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        role = getattr(user, 'role', False)

        # TODO
        # if role == 'employee' and not value.employees.filter(id=user.employee.id).exists():
        #     raise serializers.ValidationError({"detail":"This customer is not yours"})

        if role == 'customer' and user.customer != value:
            raise serializers.ValidationError({"detail":"As customer you can create Data only for yourself."})

        return value

    def validate_start_datetime(self, value):
        request = self.context.get("request")

        if not request.data.get('end_datetime'):
            raise serializers.ValidationError("End datetime is required for start_datetime")

        s = value
        e = datetime.strptime(request.data.get('end_datetime'), DATETIME_FORMAT)

        if request.data.get('customer'):
            # check customer
            customer_id = self.initial_data.get('customer').split('/')[-2]

            query = Appointment.objects.filter(customer__id=customer_id).filter( Q(start_datetime__lte=e) & Q(end_datetime__gte=s))
            if self.instance:
                query = query.exclude(id=self.instance.id)

            if query.exists():
                raise serializers.ValidationError({"detail": "Customer is busy in this datetime range"})

        if request.data.get('employee'):
            # check employee
            employee_id = self.initial_data.get('employee').split('/')[-2]

            query = Appointment.objects.filter(employee__id=employee_id).filter( Q(start_datetime__lte=e) & Q(end_datetime__gte=s))
            if self.instance:
                query = query.exclude(id=self.instance.id)

            if query.exists():
                raise serializers.ValidationError({"detail": "Employee is busy in this datetime range"})

        return value


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Notification
        fields = ('url', 'recipient', 'title', 'text', 'notification_datetime', 'notified', 'redirect_url')
        read_only_fields = ('url', 'notified')
        required_fields = ('recipient', 'title', 'text', 'notification_datetime')
        extra_kwargs = {field: {'required': True} for field in required_fields}

class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Review
        fields = ('url', 'author', 'recipient', 'service', 'title', 'text', 'grade', 'created_at', 'updated_at')
        read_only_fields = ('url', 'author')
        required_fields = ('recipient', 'title', 'grade')
        extra_kwargs = {field: {'required': True} for field in required_fields}


    def validate_recipient(self, value):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        if not user or value.id == user.id:
            raise serializers.ValidationError("You can not make reviews for yourself.")

        return value
