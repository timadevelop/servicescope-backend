from rest_framework import permissions

from .models import Message, MessageImage, Conversation

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        # TODO
        return True

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if isinstance(obj, Message):
            return obj.author.id == request.user.id
        if isinstance(obj, Conversation):
            return obj.users.filter(id=request.user.id)
        if isinstance(obj, MessageImage):
            return False # TODO?
        # no.
        return False