"""Permissions"""
from rest_framework import permissions
from .models import Feedback

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        # TODO
        return True

    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if isinstance(obj, Feedback):
            return False

        # no.
        return False

class IsOwnerOrReadOnly(IsOwner):
    """TODO"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super(IsOwnerOrReadOnly, self).has_object_permission(request, view, obj)
