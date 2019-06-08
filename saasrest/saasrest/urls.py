"""saasrest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_auth.registration.views import VerifyEmailView, RegisterView
from allauth.account.views import email_verification_sent, confirm_email as allauthemailconfirmation
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework import routers

import authentication.urls
import categories.urls
import feedback.urls
import locations.urls
import messaging.urls
import notifications.urls
import payments.urls
import public_configs.urls
import services.urls
import tags.urls
import votes.urls
#
# routers
#
router = routers.DefaultRouter()
# router.register(r'votes', views.VoteViewSet)

# router.register(r'feedback', views.FeedbackViewSet)

# router.register(r'offers', views.OfferViewSet)

# router.register(r'notifications', views.NotificationViewSet)
# router.register(r'reviews', views.ReviewViewSet)


# # payments (stripe)
# router.register(r'payments', views.PaymentsViewSet, basename='payments')
# # config
# router.register(r'config', views.ConfigViewSet, basename='config')


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.


# urlpatterns = [
# path('', include('rest_auth.urls')),
# path('login/', LoginView.as_view(), name='account_login'),
# path('registration/', include('rest_auth.registration.urls')),
# path('registration/', RegisterView.as_view(), name='account_signup'),


urlpatterns = [
    url(r'^saas_api/', include([
        path('admin/', admin.site.urls),
        url(r'auth/', include('rest_framework_social_oauth2.urls')),
        # url(r'', include(router.urls)),
        url(r'', include(authentication.urls)),
        url(r'', include(categories.urls)),
        url(r'', include(locations.urls)),
        url(r'', include(feedback.urls)),
        url(r'', include(messaging.urls)),
        url(r'', include(notifications.urls)),
        url(r'', include(payments.urls)),
        url(r'', include(public_configs.urls)),
        url(r'', include(services.urls)),
        url(r'', include(tags.urls)),
        url(r'', include(votes.urls)),
        # url(r'^rest-auth/', include('rest_auth.urls')),
        url(r'auth/registration/',
            include('rest_auth.registration.urls')),
        url(r'^auth/account-confirm-email/(?P<key>[-:\w]+)/$', allauthemailconfirmation,
            name='account_confirm_email'),
        url(r'^auth/account-confirm-email/', email_verification_sent,
            name='account_email_verification_sent'),
    ]))
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
