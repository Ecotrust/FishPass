from django.contrib import admin

from .models import *

from django.contrib.gis import admin as geoadmin
from django.contrib.gis.admin import GeoModelAdmin, OSMGeoAdmin

class BarrierAdmin(OSMGeoAdmin):
    list_display = ('pad_id', 'site_name', 'site_type', 'barrier_status', 'stream_name', 'tributary_to', 'county', 'huc12_name', 'huc10_name')
    search_fields = ['pad_id', 'site_name', 'site_type__name', 'barrier_status__name', 'stream_name', 'tributary_to', 'county', 'huc12_name', 'huc10_name']

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'description', 'budget', 'min_budget', 'max_budget',)
    search_fields = ['name', 'user', 'description']

class FocusAreaAdmin(OSMGeoAdmin):
    list_display = ('unit_id', 'description', 'unit_type')
    search_fields = ['unit_id', 'description', 'unit_type']

class BarrierTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_default_cost', 'formatted_default_post_passability', 'fixable','barrier_specific','order')
    search_fields = ['name']
    ordering = ('order',)

    def formatted_default_cost(self, obj):
        if obj.default_cost:
            return '${:,.0f}'.format(obj.default_cost)
        elif obj.barrier_specific:
            return 'Barrier Specific'
        elif not obj.fixable:
            return 'NA'
        else:
            return '-'
    formatted_default_cost.admin_order_field = 'default_cost'
    formatted_default_cost.short_description = 'Default Cost'

    def formatted_default_post_passability(self, obj):
        if type(obj.default_post_passability) == float:
            return float(obj.default_post_passability)
        else:
            return 'NA'
    formatted_default_post_passability.admin_order_field = 'default_post_passability'
    formatted_default_post_passability.short_description = 'Default Post Passability'

class BarrierStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_default_pre_passability', 'order')
    search_fields = ['name']
    ordering = ('order',)

    def formatted_default_pre_passability(self, obj):
        if type(obj.default_pre_passability) == float:
            return float(obj.default_pre_passability)
        else:
            return 'NA'
    formatted_default_pre_passability.admin_order_field = 'default_pre_passability'
    formatted_default_pre_passability.short_description = 'Default Pre Passability'

class OwnershipTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order')
    search_fields = ['name']
    ordering = ('order',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['id']
        else:
            return []

class BarrierCostAdmin(admin.ModelAdmin):
    list_display = ('pad_id', 'cost')
    search_fields = ['pad_id']
    ordering = ('pad_id',)

    def formatted_cost(self, obj):
        if obj.cost:
            return '${:,.0f}'.format(obj.cost)
        else:
            return '-'
    formatted_cost.admin_order_field = 'cost'
    formatted_cost.short_description = 'Cost'


# blatantly ripped off from Anatolij at https://stackoverflow.com/a/18559785/706797
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.db import models

from ckeditor.widgets import CKEditorWidget

class FlatPageCustom(FlatPageAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageCustom)

geoadmin.site.register(Barrier, BarrierAdmin)
geoadmin.site.register(BarrierType, BarrierTypeAdmin)
geoadmin.site.register(BarrierStatus, BarrierStatusAdmin)
geoadmin.site.register(BarrierCost, BarrierCostAdmin)
geoadmin.site.register(OwnershipType, OwnershipTypeAdmin)
geoadmin.site.register(Project, ProjectAdmin)
geoadmin.site.register(FocusArea, FocusAreaAdmin)
