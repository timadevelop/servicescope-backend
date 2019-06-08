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


class UserViewSet(viewsets.ModelViewSet):
    """
    /users view set
    """
    queryset = User.objects.order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrReadOnly, )

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = PrivateUserSerializer(instance=request.user, many=False, context={'request': request})
        return Response(serializer.data)


# class CustomRegisterView(RegisterView):
#     """
#     register view
#     """
#     queryset = User.objects.all()
