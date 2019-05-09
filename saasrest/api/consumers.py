from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer

import json

class ChatConsumer(AsyncJsonWebsocketConsumer):
    user_token = None
    room_group_name = None

    async def connect(self):
        self.user = self.scope["user"]

        if "token" in self.scope:
            self.user_token = self.scope["token"]

        # print(self.user, self.user_token)

        # guard
        if not self.user or self.user.is_anonymous:
            await self.close()
        else:
            # Join room group
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = 'chat_%s' % self.room_name

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # must be the same as token
            try:
                protocol = self.scope['subprotocols'][0]
                await self.accept(protocol)
            except:
                self.close()

    async def receive_json(self, content, **kwargs):
        """
        This handles data sent over the wire from the client.

        We need to validate that the received data is of the correct
        form. You can do this with a simple DRF serializer.

        We then need to use that validated data to confirm that the
        requesting user (available in self.scope["user"] because of
        the use of channels.auth.AuthMiddlewareStack in routing) is
        allowed to subscribe to the requested object.
        """
        message = content['message']
        print(content)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )


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
        # Leave room group
        if self.room_group_name and self.channel_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send_json({
            'message': message
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


