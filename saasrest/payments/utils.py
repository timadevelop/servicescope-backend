from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from authentication.models import User
from services.models import Service


def promote_service(user_id, service_id, days, intent_id):
    """Promotes service"""
    print('promoting service...{}'.format(service_id))

    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            print('error getting user')

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        # TODO: log!
        print('error getting service')
        return

    if not service:
        return

    service_promotion = service.promote(user, intent_id, days)
    return service, service_promotion


def send_confirmation_email(service, service_promotion, intent):
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
            [service_promotion.author.email],
            fail_silently=False,
            html_message=msg_html
        )
    except:
        return False

    return True
