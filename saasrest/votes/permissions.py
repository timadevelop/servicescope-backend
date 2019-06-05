from rest_framework import permissions
# from django.contrib.auth.models import User

from .models import Vote


class IsVoteOwner(permissions.BasePermission):
    """Is owner of vote"""

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):

        if isinstance(obj, Vote):
            return obj.user == request.user

        # no.
        return False


class IsVoteOwnerOrReadOnly(IsVoteOwner):
    """Is vote owner or read only"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super(IsVoteOwnerOrReadOnly, self).has_object_permission(request, view, obj)
