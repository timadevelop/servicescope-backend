from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_email_validation(strategy, backend, code, partial_token):
    print(strategy, backend, code, partial_token)
    # """Sends email confirmation email"""

    # msg_plain = render_to_string(
    #     'templates/email_confirmation.txt',
    #     {'service': None})

    # msg_html = render_to_string(
    #     'templates/email_confirmation.html',
    #     {'service': None})

    # try:
    #     send_mail(
    #         'Completed order',
    #         msg_plain,
    #         settings.EMAIL_HOST_USER,
    #         ['timadevelop@gmail.com'],
    #         fail_silently=False,
    #         html_message=msg_html
    #     )
    # except:
    #     return False

    return True
