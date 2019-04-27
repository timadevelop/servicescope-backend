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
# add models to django admin
#
admin.site.register(models.User)
admin.site.register(models.Service)
admin.site.register(models.Notification)

from import_export.admin import ImportExportModelAdmin

from import_export.results import RowResult


from import_export import resources
class LocationResource(resources.ModelResource):

    class Meta:
        model = models.Location
        import_id_fields = ('ekatte',)
        skip_unchanged = True
        report_skipped = False
        # raise_errors = False
        fields = ('ekatte', 't_v_m', 'name', 'oblast', 'obstina', 'kmetstvo', 'kind', 'category', 'altitude')

class LocationAdmin(ImportExportModelAdmin):
    resource_class = LocationResource

class DistrictResource(resources.ModelResource):

    class Meta:
        model = models.District
        import_id_fields = ('oblast',)
        skip_unchanged = True
        report_skipped = False
        # raise_errors = False
        fields = ('id', 'url', 'oblast', 'ekatte', 'name', 'region', )

class DistrictAdmin(ImportExportModelAdmin):
    resource_class = DistrictResource

admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.District, DistrictAdmin)
#
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

