from django.db import models
from django.conf import settings
from scenarios.models import Scenario#, PlanningUnit
from django.contrib.gis.db import models as gismodels
from django.core.validators import MaxValueValidator, MinValueValidator

GEOMETRY_DB_SRID = settings.GEOMETRY_DB_SRID

# Create your models here.
class BarrierType(models.Model):
    name = models.CharField(max_length=80)
    default_cost = models.FloatField(null=True,blank=True,verbose_name="Default Cost of Mitigation")
    default_post_passability = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],default=1.0,verbose_name='Post-passability')

class BarrierStatus(models.Model):
    name = models.CharField(max_length=90)
    default_pre_passability = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],default=1.0, verbose_name='Pre-passability')

class OwnershipType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

class Barrier(models.Model):
    # PAD_ID
    pad_id = models.IntegerField(primary_key=True,verbose_name="Barrier ID",help_text="The barrier ID as assigned in the PAD")
    # PassageID - ???
    passage_id = models.IntegerField(verbose_name="Passage ID")
    # StreamName
    stream_name = models.CharField(max_length=255,verbose_name="Stream Name",help_text="The name of the waterbody obstructed by this barrier")
    # TributaryTo
    tributary_to = models.CharField(max_length=255,verbose_name="Tributary To",help_text="The waterbody that this obstructed waterbody flows into")
    # SiteName
    site_name = models.CharField(max_length=255,verbose_name="Site Name",help_text="Name of the site at which barrier is located, or name of the barrier itself")
    # SiteType
    site_type = models.ForeignKey(BarrierType,verbose_name="Barrier Type",)
    # BarStatus
    barrier_status = models.ForeignKey(BarrierStatus,verbose_name="Barrier Status")
    # Protocol
    protocol = models.CharField(max_length=255,verbose_name="Protocol",help_text="How the barrier was identified")
    # AssessedBy
    assessed_by = models.CharField(max_length=255,verbose_name="Assessed By")
    #TODO: determine HUC codes, etc... by lat/lon intersection with FocusAreas
    #HUC8_Code
    huc8_code = models.IntegerField(null=True,blank=True,default=None,verbose_name="HUC 8 ID")
    #HUC8_Name
    huc8_name = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="HUC 8 Name")
    #HUC10_Code
    huc10_code = models.IntegerField(null=True,blank=True,default=None,verbose_name="HUC 10 ID")
    #HUC10_Name
    huc10_name = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="HUC 10 Name")
    #HUC12_Code
    huc12_code = models.BigIntegerField(null=True,blank=True,default=None,verbose_name="HUC 12 ID")
    #HUC12_Name
    huc12_name = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="HUC 12 Name")
    #County
    county = models.CharField(max_length=100,null=True,blank=True,default=None,verbose_name="County")
    # OwnershipType
    ownership_type = models.ForeignKey(OwnershipType,null=True,blank=True,default=None,verbose_name="Ownership Type")
    # NHDCOMID
    nhd_com_id = models.IntegerField(null=True,blank=True,default=None)
    # NHDComMeas
    nhd_com_meas = models.FloatField(null=True,blank=True,default=None)
    # Point_X
    longitude = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],verbose_name="Longitude (x value)")
    # Point_Y
    latitude = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],verbose_name="Latitude (y value)")
    # State
    state = models.CharField(max_length=5,default="CA")
    # Updated (YYYY-MM-DD)
    updated = models.DateField(null=True,blank=True,default=None,verbose_name="Date Updated")
    # ESU_COHO
    esu_coho = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="Coho Salmon ESU",help_text="Evolutionarily Significant Unit")
    # ESU_CHIN
    esu_chinook = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="Chinook Salmon ESU",help_text="Evolutionarily Significant Unit")
    # ESU_STEEL
    esu_steelhead = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="Steelhead Salmon ESU",help_text="Evolutionarily Significant Unit")
    # Miles_Upst
    upstream_miles = models.FloatField(validators=[MinValueValidator(0.0)],default=0,verbose_name="Miles Upstream")
    # DS_ID
    # RDH - this would be better as a ForeignKey to self, but we cannot guarantee that the downstream barrier will be created first, so Integer is best for now.
    downstream_id = models.IntegerField(null=True,blank=True,default=None,verbose_name="Downstream Barrier ID")
    # DS_Barrier
    downstream_barrier_count = models.IntegerField(validators=[MinValueValidator(0)],default=0,verbose_name="Downstream Barrier Count")

class Project(Scenario):
    class Options:
        verbose_name = 'Project'
        # icon_url = 'marco/img/multi.png'
        form = 'fishpass.forms.ProjectForm'
        form_template = 'scenarios/form.html'
        # form_template = 'fishpass/project_form.html'
        show_template = 'scenarios/show.html'

# outside of scenario model, between pad and user entry
#class ScenarioBarrier(models.Model):
#class ScenarioBarrierType(models.Model):
#class ScenarioBarrierStatus(models.Model):

#class Default(models.Model):
#class DefaultCost(models.Model):

################
# QUESTIONABLE #
################
#class BarrierType(models.Model):
#class BarrierStatus(models.Model):

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
