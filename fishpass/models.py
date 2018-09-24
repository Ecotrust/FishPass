from django.db import models
from django.conf import settings
from scenarios.models import Scenario, PlanningUnit
from django.contrib.gis.db import models as gismodels



GEOMETRY_DB_SRID = settings.GEOMETRY_DB_SRID

# Create your models here.

#class Barrier(PlanningUnit)
#class ScenarioBarrier(Scenario)
#class ScenarioBarrierType()
#class ScenarioBarrierStatus()
#class Default
#class DefaultCost


class FocusArea(models.Model):
    UNIT_TYPE_CHOICES = []
    for type in settings.FOCUS_AREA_TYPES:
        UNIT_TYPE_CHOICES.append((type, type))

    unit_type = models.CharField(max_length=20, null=True, blank=True, default=None, choices=UNIT_TYPE_CHOICES)

    # The HUC/County/Region ID
    unit_id = models.CharField(max_length=100, null=True, blank=True, default=None)

    description = models.CharField(max_length=255, null=True, blank=True, default=None)

    geometry = gismodels.MultiPolygonField(srid=GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Focus Area Geometry")

    objects = gismodels.GeoManager()

    def __str__(self):
        if self.description:
            return self.description
        else:
            return '%s: %s' % (self.unit_type, self.unit_id)

    def __unicode__(self):
        if self.description:
            return u'%s' % self.description
        else:
            return u'%s: %s' % (self.unit_type, self.unit_id)
