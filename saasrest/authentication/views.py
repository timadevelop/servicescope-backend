"""
Views auth & users
"""
from rest_auth.registration.views import RegisterView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# TODO
from saas_core.permissions import IsOwnerOrReadOnly

from .models import User
from .serializers import UserSerializer, PrivateUserSerializer

from saas_core.config import DEFAULT_PERMISSION_CLASSES

class UserViewSet(viewsets.ModelViewSet):
    """
    /users view set
    """
    queryset = User.objects.order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = DEFAULT_PERMISSION_CLASSES + [IsOwnerOrReadOnly, ]

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        context = self.get_serializer_context()
        kwargs['context'] = context
        # if isinstance(args[0], list):
        #     serializer_class = self.get_serializer_class()
        if len(args) > 0 and isinstance(args[0], User) and context['request'].user and context['request'].user.id == args[0].id:
            serializer_class = PrivateUserSerializer
        else:
            serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = PrivateUserSerializer(
            instance=request.user, many=False, context={'request': request})
        return Response(serializer.data)


# class CustomRegisterView(RegisterView):
#     """
#     register view
#     """
#     queryset = User.objects.all()
