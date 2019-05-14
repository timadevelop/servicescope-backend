from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer

import json

from channels.db import database_sync_to_async


from channels.layers import get_channel_layer

import api.models as models

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



class ChatConsumer(AsyncJsonWebsocketConsumer):
    user_token = None
    room_group_name = None

    @database_sync_to_async
    def get_conversation(self, id):
        try:
            conv = models.Conversation.objects.get(id=id)
            return conv
        except:
            return None

    @database_sync_to_async
    def get_msg(self):
        try:
            result = models.Message.objects.all()[0]
            return result
        except:
            return None

    async def connect(self):
        self.user = self.scope["user"]

        if "token" in self.scope:
            self.user_token = self.scope["token"]

        # guard
        if not self.user or self.user.is_anonymous:
            await self.close()
        else:
            try:
                protocol = self.scope['subprotocols'][0]
                await self.accept(protocol)
                await self.notify_using_channel_layer({
                    "type": "connected",
                    "payload": None
                })
            except:
                await self.close()

    async def join_room(self, room_name):
        await self.leave_group()

        # Join room group
        # print('join room {}'.format(room_name))
        self.room_name = room_name

        self.conversation = await self.get_conversation(self.room_name)

        if not self.conversation or not self.conversation.users.filter(id=self.user.id).exists():
            await self.close()
        else:
            self.room_group_name = 'chat_%s' % self.room_name

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            # print('connected to room {}'.format(self.room_group_name))
            content = {
                "type": "joined_room",
                "payload": {
                    "room_name": room_name
                },
            }
            await self.notify_using_channel_layer(content)


    async def receive_json(self, content, **kwargs):
        """
        This handles data sent over the wire from the client.

        We need to validate that the received data is of the correct
        form. You can do this with a simple DRF serializer.

        We then need to use that validated data to confirm that the
        global/ng user (available in self.scope["user"] because of
        the use of channels.auth.AuthMiddlewareStack in routing) is
        allowed to subscribe to the requested object.
        """
        # message = content['message']
        print('got')
        print(content)
        if content['type'] == 'join_room_request':
            payload = content["payload"]
            room_name = payload["room_name"]
            await self.join_room(room_name)
        elif content['type'] == 'leave_room':
            await self.leave_group()

        # serializer = self.get_serializer(data=content)
        # if not serializer.is_valid():
        #     return
        # # Define this method on your serializer:
        # group_name = serializer.get_group_name()
        # # The AsyncJsonWebsocketConsumer parent class has a
        # # self.groups list already. It uses it in cleanup.
        # self.groups.append(group_name)
        # # This actually subscribes the requesting socket to the
        # # named group:
        # await self.channel_layer.group_add(
        #     group_name,
        #     self.channel_name,
        # )
        #
    async def disconnect(self, close_code):
        await self.leave_group()

    async def leave_group(self):
        # Leave room group
        if self.room_group_name and self.channel_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def notify_using_channel_layer(self, content):
        await self.channel_layer.send(self.channel_name, {
            "type": "notify",
            "content": content,
        })

    async def notify(self, event):
        """
        This handles calls elsewhere in this codebase that look
        like:

            channel_layer.group_send(group_name, {
                'type': 'notify',  # This routes it to this handler.
                'content': json_message,
            })

        Don't try to directly use send_json or anything; this
        decoupling will help you as things grow.
        """
        await self.send_json(event["content"])
