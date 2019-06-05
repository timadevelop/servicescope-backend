"""Serializers"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import serializers

from asgiref.sync import async_to_sync
from saas_core.utils import notify_user

from .models import Notification


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    """Notification serializer"""
    # recipient_id = serializers.SerializerMethodField()
    # conversation_id = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'url', 'recipient', 'conversation', 'conversation_id',
                  'recipient_id', 'title', 'type', 'text', 'notification_datetime',
                  'notified', 'redirect_url', 'created_at', 'updated_at')
        read_only_fields = ('id', 'url', 'notified')
        required_fields = ('recipient', 'title', 'text',
                           'notification_datetime')
        extra_kwargs = {field: {'required': True} for field in required_fields}

    # def get_recipient_id(self, instance):
    #     recipient = getattr(instance, 'recipient', None)
    #     if recipient:
    #         return recipient.id
    #     else:
    #         return None

    # def get_conversation_id(self, instance):
    #     conversation = getattr(instance, 'conversation', None)
    #     if conversation:
    #         return conversation.id
    #     else:
    #         return None

    # def create(self, validated_data):
    #     obj = models.Notification.objects.create(**validated_data)
    #     return obj
    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     if (self.context['request']) and getattr(instance, 'conversation', False):
    #         response['conversation'] = ConversationSerializer(instance.conversation, many=False, context = self.context).data
    #     return response


# send notification
@receiver(post_save, sender=Notification, dispatch_uid='notification_post_save_signal')
def send_new_notification(sender, instance, created, **kwargs):
    def send_notification(notification):
        if not notification or not getattr(notification, 'recipient', False):
            return False
        serializer = NotificationSerializer(
            notification, many=False, context={'request': None})
        async_to_sync(notify_user)(notification.recipient.id, serializer.data)

    if created:
        send_notification(instance)
