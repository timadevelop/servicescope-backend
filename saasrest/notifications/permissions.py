"""Notifications permissions"""
from rest_framework import permissions

from .models import Notification


class IsOwner(permissions.BasePermission):
    """Is owner for notifications"""
    def has_permission(self, request, view):
        # TODO
        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if isinstance(obj, Notification):
            return obj.recipient.id == request.user.id
        # no.
        return False


class IsOwnerOrReadOnly(IsOwner):
    """Is owner or read only for notifications"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super(IsOwnerOrReadOnly, self).has_object_permission(request, view, obj)
