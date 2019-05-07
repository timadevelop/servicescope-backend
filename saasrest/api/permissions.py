from rest_framework import permissions
# from django.contrib.auth.models import User

from .models import User, Notification, Review, \
    Location, \
    Service, ServiceImage, ServicePromotion, \
    Post, PostImage, PostPromotion, Offer, Vote
import api.models as models

class IsAdminUserOrReadOnly(permissions.IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super(
            IsAdminUserOrReadOnly, 
            self).has_permission(request, view)
        # Python3: is_admin = super().has_permission(request, view)
        return request.method in permissions.SAFE_METHODS or is_admin


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        print('is_owner1')
        return True

    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        print('is_owner')
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if isinstance(obj, User):
            # only user can edit himself
            if obj == request.user:
                return True
            else:
                return False

        if isinstance(obj, Review):
            return obj.author == request.user
        if isinstance(obj, Service):
            return obj.author == request.user
        if isinstance(obj, ServiceImage):
            return obj.service.author == request.user
        if isinstance(obj, ServicePromotion):
            return obj.author == request.user
        if isinstance(obj, Post):
            return obj.author == request.user
        if isinstance(obj, PostImage):
            return obj.post.author == request.user
        if isinstance(obj, PostPromotion):
            return obj.author == request.user
        if isinstance(obj, Offer):
            return obj.author == request.user
        if isinstance(obj, Vote):
            return obj.user == request.user
        if isinstance(obj, models.Message):
            return obj.message.conversation.users.filter(id=request.user.id)
        if isinstance(obj, models.Conversation):
            return obj.users.filter(id=request.user.id)
        if isinstance(obj, models.MessageImage):
            return False #?

        # no.
        return False

class IsOwnerOrReadOnly(IsOwner):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super(IsOwner, self).has_object_permission(request, view, obj)
