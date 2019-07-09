from rest_framework import permissions
from .models import Service, ServicePromotion



class IsOwner(permissions.BasePermission):
    """Is owner of service"""
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):

        if isinstance(obj, Service):
            return obj.author == request.user
        if isinstance(obj, ServicePromotion):
            return obj.author == request.user

        # no.
        return False


class IsOwnerOrReadOnly(IsOwner):
    """Is service owner or read only"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super(IsOwnerOrReadOnly, self).has_object_permission(request, view, obj)
