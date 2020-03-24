def create_superuser(email, password):
    from authentication.models import User
    print('Trying to create superuser with email={}'.format(email))

    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(email, password)
        print('Superuser created.')
    else:
        print('Superuser creation skipped.')

# Creates oauth2_provider application
# More info: https://github.com/jazzband/django-oauth-toolkit/blob/master/oauth2_provider/models.py
def create_oauth2_provider_app(email):
    from authentication.models import User
    from oauth2_provider.models import Application

    admin_user = User.objects.get(email=email)

    client_id = os.environ.get('API_CLIENT_ID')
    client_secret = os.environ.get('API_CLIENT_SECRET')

    if not Application.objects.exists():
        application = Application.objects.create(
            client_id=client_id,
            client_secret=client_secret,
            user=admin_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            name='password-based app')

        print('Created OAuth2 app.')
    else:
        print('OAuth2 app creation skipped.')


# Dhango admin credentials (change them)
PASSWORD= os.environ.get('DJANGO_ADMIN_PASSWORD')
EMAIL=os.environ.get('DJANGO_ADMIN_EMAIL')

create_superuser(EMAIL, PASSWORD)
create_oauth2_provider_app(EMAIL)