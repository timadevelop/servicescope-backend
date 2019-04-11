from rest_framework import permissions
# from django.contrib.auth.models import User
from .models import User, Business, Customer, Employee,  Appointment, Appeal, \
    Service, Inventory, InventoryItem, Review

class IsAdminUserOrReadOnly(permissions.IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super(
            IsAdminUserOrReadOnly, 
            self).has_permission(request, view)
        # Python3: is_admin = super().has_permission(request, view)
        return request.method in permissions.SAFE_METHODS or is_admin


class IsEmployeeOrCustomerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # (filtering is applied in view)
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.role == 'employee' or request.user.role == 'customer':
            return True

        # no.
        return False

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # (filtering is applied in view)
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.role == 'employee' and getattr(obj, 'employee', None) == request.user.employee:
            return True

        if request.user.role == 'customer' and getattr(obj, 'customer', None) == request.user.customer:
            return True

        # no.
        return False


class IsEmployeeOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # (filtering is applied in view)
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.role == 'employee':
            return True

        # no.
        return False

class IsBusinessOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'business'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.role == 'business'

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_permission(self, request, view):
        return True
        return request.user and request.user.role == 'business'

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        print('isOwnerorreadonly')
        if request.method in permissions.SAFE_METHODS:
            return True

        # obj is user
        if isinstance(obj, User):
            # only user can edit himself
            if obj == request.user:
                return True
            else:
                return False

        # obj is business
        if isinstance(obj, Business):
            return obj.user == request.user



        if (isinstance(obj, Customer)):
            if getattr(obj, 'user', False) and obj.user == request.user:
                # Customer can edit himself
                return True
            elif getattr(obj, 'owner', False):
                if request.user.role == 'business' and obj.owner == request.user.business:
                    return True
                if request.user.role == 'employee' and request.user.employee.businesses.filter(id=obj.owner.id).exists():
                    return True
                else:
                    return False
            else:
                return False

        if (isinstance(obj, Employee)):
            if obj.user == request.user:
                # Employee can edit himself
                return True
            elif getattr(obj, 'businesses', False) and obj.businesses.filter(user=request.user):
                # business can edit employees
                return True
            else:
                return False

        if (isinstance(obj, Appeal)):
            if obj.author == request.user:
                return True
            elif obj.recipient == request.user:
                return True
            else:
                return False

        if (isinstance(obj, Review)):
            if obj.author == request.user:
                return True
            else:
                return False

        # obj is service
        if isinstance(obj, Service):
            if request.user.role == 'business' and obj.business.user == request.user:
                return True
            else:
                return False

        # obj is inventory
        if isinstance(obj, Inventory):
            if request.user.role == 'business' and obj.business.user == request.user:
                return True
            if request.user.role == 'employee' and request.user.employee.businesses.filter(id=obj.business.id).exists():
                return True
            return False

        # obj is inventory
        if isinstance(obj, InventoryItem):
            if request.user.role == 'business' and obj.inventory.business.user == request.user:
                return True
            if request.user.role == 'employee' and request.user.employee.businesses.filter(id=obj.inventory.business.id).exists():
                return True
            return False

        # obj is inventory


        # obj is event
        if isinstance(obj, Appointment):
            if getattr(obj, 'employee', False) and obj.employee.user == request.user:
                # Employee can edit event assigned to him
                return True
            elif getattr(obj, 'customer', False) and getattr(obj.customer, 'profile', False) and obj.customer.user == request.user:
                # Customer can edit event assigned to him
                return True
            else:
                return False

        # no.
        return False

# class IsOwnerOrPublic(permissions.BasePermission):
#     """
#     Object-level permission to only allow owners of an object to edit it.
#     Assumes the model instance has an `owner` attribute.
#     """


#     def has_permission(self, request, view):
#         # Read permissions are disallowed to any request,

#         if request.method in permissions.SAFE_METHODS and getattr(obj, 'is_public', False):
#             return True

#         # no.
#         return False

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user.profile, 'customer')


class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user.profile, 'employee')
    # def has_object_permission(self, request, view, obj):
    #     return True
    #     if not hasattr(request.user.profile, 'employee'):
    #         return False
    #     if not hasattr(obj, 'employee'):
    #         return False
    #     return obj.employee == request.user.employee
