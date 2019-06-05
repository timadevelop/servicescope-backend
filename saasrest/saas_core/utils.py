
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from django.urls import resolve

from notifications.models import Notification
from django.core.cache import cache


@database_sync_to_async
def get_notifications(user, conversation, notified):
    return Notification.objects.filter(recipient=user).filter(conversation=conversation).filter(notified=notified)


@database_sync_to_async
def create_notification(recipient, conversation, title, text, redirect_url):
    return Notification.objects.create(recipient=recipient, conversation=conversation,
                                       title=title, text=text, redirect_url=redirect_url)


async def broadcast_message(msg, serializer_data):
    group_name = 'chat_%s' % msg.conversation.id
    channel_layer = get_channel_layer()
    content = {
        "type": "new_message",
        "payload": serializer_data,
    }
    await channel_layer.group_send(group_name, {
        "type": "notify",
        "content": content,
    })
    # create notification if user if offlie
    for user in msg.conversation.users.exclude(id=msg.author.id).all():
        if user.online < 1:
            q = await get_notifications(user, msg.conversation, False)
            if not q.exists():
                await create_notification(recipient=user, conversation=msg.conversation,
                                          title="New Message",
                                          text="New message from {}".format(
                                              msg.author),
                                          redirect_url="/messages/c/{}".format(msg.conversation.id))
        else:
            n = await create_notification(recipient=user, conversation=msg.conversation,
                                          title="New Message from {}".format(
                                              msg.author.first_name),
                                          text="{}".format(msg.text),
                                          redirect_url="/messages/c/{}".format(msg.conversation.id))
            # s = serializers.NotificationSerializer(n, many=False, context={'request': None})
            # await notify_user(user.id, s.data)


async def broadcast_deleted_message(conversationId, msgId):
    group_name = 'chat_%s' % conversationId
    channel_layer = get_channel_layer()
    content = {
        "type": "deleted_message",
        "payload": msgId,
    }
    await channel_layer.group_send(group_name, {
        "type": "notify",
        "content": content,
    })


async def send_group_notification(group_name, notification):
    channel_layer = get_channel_layer()
    content = {
        "type": "notification",
        "payload": notification,
    }
    await channel_layer.group_send(group_name, {
        "type": "notify",
        "content": content,
    })


async def notify_user(user_id, notification_serializer_data):
    channel_layer = get_channel_layer()
    await send_group_notification('user_%s' % user_id, notification_serializer_data)

"""
TODO: rename

flow:
- try to get result from context
- try to get from cache
- serialize, set to cache (for next requests) and set to context (for current request)

"""


def cached_or_new(key, serializer_class, instance, object_property_name, context, many=False):
    # try to get from context
    context_result = context.get(key)
    if context_result:
        return context_result

    # try to get from cache
    result = cache.get(key)
    if result is None:
        # ok, lets serialize and save serialized thing in our cache
        obj = getattr(instance, object_property_name, False)
        result = serializer_class(obj, many=many, context=context).data
        cache.set(key, result)

    # save in context for current request processing
    context[key] = result

    return result


def get_obj_from_url(self, url):
    return resolve(url).func.cls.serializer_class.Meta.model.objects.get(**resolve(url).kwargs)


def fix_django_headers(meta):
    """
    Fix this nonsensical API:
    https://docs.djangoproject.com/en/1.11/ref/request-response/
    https://code.djangoproject.com/ticket/20147
    """
    ret = {}
    for k, v in meta.items():
        if k.startswith("HTTP_"):
            k = k[len("HTTP_"):]
        elif k not in ("CONTENT_LENGTH", "CONTENT_TYPE"):
            # Skip CGI garbage
            continue
        ret[k.lower().replace("_", "-")] = v
    return ret
