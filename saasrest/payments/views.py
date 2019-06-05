"""Payments views"""
import json

from django.conf import settings
from django.core.mail import send_mail
from django.template.defaulttags import register
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# pylint: disable=fixme, import-error
import stripe

from authentication.models import User
from saas_core.utils import fix_django_headers
from services.models import Service, ServicePromotion


@register.filter
def get_item(dictionary, key):
    # print('get_item')
    # print(dictionary, key)
    # print('_-----------------------------____')
    return dictionary.get(key, 'None')


class PaymentsViewSet(viewsets.ViewSet):
    """
    Main view
    """
    @action(
        detail=False,
        methods=['post'],
        url_path='create_new_intent',
        permission_classes=[IsAuthenticated, ])
    def create_new_intent(self, request):
        """Endpoint for new PaymentIntent creation"""
        body = json.loads(request.body.decode())
        amount = body.get('amount', None)
        currency = body.get('currency', None)
        metadata = body.get('metadata', None)
        if not amount or not currency:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata=metadata
        )

        return Response(intent)

    def send_confirmation_email(self, service, service_promotion, intent):
        """Sends payment confirmation email"""

        msg_plain = render_to_string(
            'templates/email.txt',
            {'service': service, 'service_promotion': service_promotion})

        msg_html = render_to_string(
            'templates/completed_order_email.html',
            {'service': service, 'service_promotion': service_promotion, 'intent': intent})

        try:
            send_mail(
                'Completed order',
                msg_plain,
                settings.EMAIL_HOST_USER,
                ['timadevelop@gmail.com'],
                fail_silently=False,
                html_message=msg_html
            )
        except:
            return False

        return True

    @action(
        detail=False,
        methods=['post'],
        url_path='send_email',
        permission_classes=[IsAuthenticated, ])
    def send_email(self, request):
        """Test Endpoint for email sending"""
        body = json.loads(request.body.decode())
        amount = body.get('amount', None)
        currency = body.get('currency', None)
        metadata = body.get('metadata', None)

        msg_plain = render_to_string('templates/email.txt', {'text': 'waaat'})
        msg_html = render_to_string(
            'templates/email_1.html', {'text': 'superduper'})
        try:
            send_mail(
                'Subject here',
                msg_plain,
                settings.EMAIL_HOST_USER,
                ['recipient@gmail.com'],
                fail_silently=False,
                html_message=msg_html
            )
        except:
            return Response({'success': 'false'})

        return Response({'success': 'true'})

    @action(
        detail=False,
        methods=['post'],
        url_path='update_intent',
        permission_classes=[IsAuthenticated, ])
    def update_intent(self, request):
        """Update payment intent endpoint"""
        body = json.loads(request.body.decode())
        intent_id = body.get('id', None)
        amount = body.get('amount', None)
        currency = body.get('currency', None)
        metadata = body.get('metadata', None)

        if not intent_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        intent = stripe.PaymentIntent.modify(
            intent_id,
            amount=amount,
            currency=currency,
            metadata=metadata
        )

        return Response(intent)

    @action(detail=False, methods=['post'], url_path='webhook')
    def webhook(self, request):
        """Stripe webhook"""
        # TODO: accept only stripe check
        payload = request.body
        headers = request.META

        sig_header = fix_django_headers(
            headers).get('stripe-signature', None)
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_ENDPOINT_SECRET
            )
        except ValueError:
            # invalid payload
            print('invalid payload')
            return Response({"detail": 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            # invalid signature
            print('invalid signature')
            return Response({"detail": 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        event_dict = event.to_dict()
        if event_dict['type'] == "payment_intent.succeeded":
            intent = event_dict['data']['object']
            print("Succeeded: ", intent['id'])
            print("Succeeded metadata: ", intent['metadata'])
            # Fulfill the customer's purchase
            self.process_succeeded_intent(intent)
        elif event_dict['type'] == "payment_intent.payment_failed":
            intent = event_dict['data']['object']
            if intent.get('last_payment_error'):
                error_message = intent['last_payment_error']['message']
            else:
                error_message = None

            print("Failed: ", intent['id'], error_message)
            # TODO: Notify the customer that payment failed
        return Response(status=status.HTTP_200_OK)

    def process_succeeded_intent(self, intent):
        """Process Succeded paymentIntent"""
        metadata = intent['metadata']

        reason = metadata.get('reason', None)
        if not reason:
            print('strange!')
            # TODO
            return

        if reason == 'promote_service':
            service, service_promotion = self.promote_service(intent)
            # Send email
            self.send_confirmation_email(service, service_promotion, intent)
        elif reason == 'promote_post':
            # TODO
            pass

    def promote_service(self, intent):
        """Promotes service using intent"""
        metadata = intent['metadata']

        print('promoting service...')
        user_id = int(metadata.get('user_id', None))
        # model = metadata.get('model', None)
        model_id = int(metadata.get('model_id', None))
        # plan = metadata.get('plan', None)
        days = int(metadata.get('days', None))

        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except Exception as e:
                print('error getting user', e)

        try:
            service = Service.objects.get(id=model_id)
        except:
            print('error getting service')
            return

        if not service:
            return

        if service.promotions.exists():
            print('update old promotion')
            service_promotion = service.promotions.first()
            # add days
            service_promotion.end_datetime = service_promotion.end_datetime + \
                timezone.timedelta(days=days)
            service_promotion.stripe_payment_intents.append(intent['id'])
            service_promotion.save()
            print('success')
        else:
            print('create new promotion')
            end_datetime = timezone.now() + timezone.timedelta(days=days)
            service_promotion = ServicePromotion.objects.create(
                author=user, service=service,
                stripe_payment_intents=[intent['id']],
                end_datetime=end_datetime)
            print('success')

        service.promoted_til = service_promotion.end_datetime
        service.save()
        return service, service_promotion
