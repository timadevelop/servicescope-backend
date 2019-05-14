from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from django.conf.urls import url

from . import consumers

from channels.auth import AuthMiddlewareStack
# from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser

from oauth2_provider.models import AccessToken


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        headers = dict(scope['headers'])
        if b'sec-websocket-protocol' in headers:
            try:
                token_key = headers[b'sec-websocket-protocol'].decode()
                token = AccessToken.objects.get(token=token_key)
                scope['user'] = token.user
                scope['token'] = token
            except AccessToken.DoesNotExist:
                scope['user'] = AnonymousUser()
        return self.inner(scope)

TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))

websocket_urlpatterns = [
    url(r'^ws/global/$', consumers.ChatConsumer),
]

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

