from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from authentication.models import User
from services.models import Service

import logging
logger = logging.getLogger(__name__)


PROMOTION_REASONS = [
    "promote_service",
    # "promote_post"
]

SERVICE_PROMOTIONS_PLANS = {
    "pro": {
        'days': 7,
        'amount': 403,
        'currency': 'bgn'
    },
    "basic": {
        'days': 3,
        'amount': 274,
        'currency': 'bgn'
    }
}


def is_valid_payment_intent(plan, days, amount, currency, reason):
    plan_details = SERVICE_PROMOTIONS_PLANS.get(plan, None)
    if not plan_details:
        return False

    if days != plan_details.get('days'):
        return False

    if amount != plan_details.get('amount') or currency != plan_details.get('currency'):
        return False

    if reason not in PROMOTION_REASONS:
        return False

    return True


def promote_service(user_id, service_id, days, intent_id):
    """Promotes service"""
    logger.info('Promoting service...{}'.format(service_id))

    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning("User does not exists")

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        logger.error('Error getting service for promotion. Given service id: {}'.format(service_id))
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
        logger.error("Error sending order confirmation email. Service Promotion #{}, intent: {}".format(service_promotion.pk, str(intent)))
        return False

    return True
