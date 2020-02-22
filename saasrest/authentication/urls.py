"""
Authentication views
"""
from rest_framework import routers
from django.conf.urls import url, include
from django.urls import path

from . import views



from rest_auth.views import (
    LoginView, LogoutView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)

from rest_auth.registration.views import VerifyEmailView, RegisterView
from allauth.account.views import email_verification_sent, confirm_email as allauthemailconfirmation, PasswordResetView

ROUTER = routers.DefaultRouter()
ROUTER.register(r'users', views.UserViewSet, base_name="user")
# ROUTER.register(r'', views.UserViewSet, base_name="user")


urlpatterns = [
    url(r'', include(ROUTER.urls)),
    url(r'auth/', include('rest_framework_social_oauth2.urls')),
    url(r'rest-auth/', include('rest_auth.urls')),
    url(r'auth/registration/',
    include('rest_auth.registration.urls')),
      path('accounts/', include('allauth.urls')),

    url(r'^auth/account-confirm-email/(?P<key>[-:\w]+)/$', allauthemailconfirmation,
        name='account_confirm_email'),
    url(r'^auth/account-confirm-email/', email_verification_sent,
        name='account_email_verification_sent'),
]
