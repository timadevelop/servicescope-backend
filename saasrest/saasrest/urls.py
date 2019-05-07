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
from django.contrib import admin
from django.urls import path

from django.conf.urls import url, include
from rest_framework import routers
from api import views
from api import models


from django.conf.urls.static import static
from django.conf import settings

#
# routers
#
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'districts', views.DistrictViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'service-promotions', views.ServicePromotionViewSet)
router.register(r'service-images', views.ServiceImageViewSet)
router.register(r'votes', views.VoteViewSet)

router.register(r'offers', views.OfferViewSet)

router.register(r'notifications', views.NotificationViewSet)
router.register(r'reviews', views.ReviewViewSet)

router.register(r'conversations', views.ConversationViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'message-images', views.MessageImageViewSet)
#
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('saas_api/admin/', admin.site.urls),
    url(r'^saas_api/auth/', include('rest_framework_social_oauth2.urls')),
    url(r'^saas_api/', include(router.urls)),

    # url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^saas_api/auth/registration/', include('rest_auth.registration.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

