from django.contrib import admin
from api import models

# Register your models here.
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
