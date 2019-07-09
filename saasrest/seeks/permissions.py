from rest_framework import permissions
# from django.contrib.auth.models import User


from .models import Seeking, SeekingPromotion


class IsOwner(permissions.BasePermission):
    """Is owner of seeking"""
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):

        if isinstance(obj, Seeking):
            return obj.author == request.user
        if isinstance(obj, SeekingPromotion):
            return obj.author == request.user

        # no.
        return False


class IsOwnerOrReadOnly(IsOwner):
    """Is seeking owner or read only"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super(IsOwnerOrReadOnly, self).has_object_permission(request, view, obj)
