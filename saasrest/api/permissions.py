from rest_framework import permissions
# from django.contrib.auth.models import User

from .models import User, Notification, Review, \
    Location, \
    Service, ServiceImage, ServicePromotion, \
    Post, PostImage, PostPromotion, Offer, Vote

class IsAdminUserOrReadOnly(permissions.IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super(
            IsAdminUserOrReadOnly, 
            self).has_permission(request, view)
        # Python3: is_admin = super().has_permission(request, view)
        return request.method in permissions.SAFE_METHODS or is_admin


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
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

        # no.
        return False
