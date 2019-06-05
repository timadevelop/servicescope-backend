from django.contrib import admin

from .models import Service, ServicePromotion
# Register your models here.

admin.site.register(Service)
admin.site.register(ServicePromotion)
