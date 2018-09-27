from django.db import models
from django.conf import settings
from features.registry import register
from scenarios.models import Scenario#, PlanningUnit
from django.contrib.gis.db import models as gismodels
from django.core.validators import MaxValueValidator, MinValueValidator

GEOMETRY_DB_SRID = settings.GEOMETRY_DB_SRID

# Create your models here.
class BarrierType(models.Model):
    name = models.CharField(max_length=80)
    default_cost = models.FloatField(null=True,blank=True,verbose_name="Default Cost of Mitigation")
    default_post_passability = models.FloatField(null=True,blank=True,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],default=1.0,verbose_name='Post-passability')
    fixable = models.BooleanField(default=True)
    barrier_specific = models.BooleanField(default=False)
    order = models.IntegerField(default=999)

    def __str__(self):
        return self.name

class BarrierStatus(models.Model):
    name = models.CharField(max_length=90)
    default_pre_passability = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],default=1.0, verbose_name='Pre-passability')
    order = models.IntegerField(default=999)

    def __str__(self):
        return self.name

class OwnershipType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    order = models.IntegerField(default=999)

    def __str__(self):
        return self.name

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
    geometry = gismodels.PointField(null=True,blank=True,default=None,srid=settings.GEOMETRY_DB_SRID)

    def to_dict(self, project=None):
        # Calculate any project overrides
        override_fields = {
            'estimated_cost': self.site_type.default_cost,
            'pre_passability': self.barrier_status.default_pre_passability,
            'post_passability': self.site_type.default_post_passability,
            # TODO: Perhaps: if not fixable, cost = NA, post_passability = 0, action = 'exclude'
            'fixable': self.site_type.fixable,
            'action': 'consider'
        }
        if self.site_type.barrier_specific:
            override_fields['estimated_cost'] = 'Barrier Specific',
        if project:
            override_type_list = ScenarioBarrierType.objects.filter(barrier_type=feature.barrier_type,project=project)
            if override_type_list.count() > 0:
                override_type = override_type_list[0]
                if override_type.default_cost:
                    override_fields['estimated_cost'] = override_type.default_cost
                elif override_type.barrier_specific:
                    override_fields['estimated_cost'] = 'Barrier Specific'
                if override_type.default_post_passability:
                    override_fields['post_passability'] = override_type.default_post_passability
                override_fields['fixable'] = override_type.fixable
            override_status_list = ScenarioBarrierStatus.objects.filter(barrier_status=feature.barrier_status,project=project)
            if override_status_list.count() > 0:
                override_status = override_status_list[0]
                if override_status.default_pre_passability:
                    override_fields['pre_passability'] = override_status.default_pre_passability
            override_barrier_list = ScenarioBarrier.objects.filter(barrier=self,project=project)
            if override_barrier_list.count() > 0:
                override_barrier = override_barrier_list[0]
                if override_barrier.pre_pass:
                    override_fields['pre_passability'] = override_barrier.pre_pass
                if override_barrier.post_pass:
                    override_fields['post_passability'] = override_barrier.post_pass
                if override_barrier.cost:
                    override_fields['estimated_cost'] = override_barrier.cost
                if override_barrier.action:
                    override_fields['action'] = override_barrier.action


        return {
            'pad_id': self.pad_id,
            'passage_id': self.passage_id,
            'stream_name': self.stream_name,
            'tributary_to': self.tributary_to,
            'site_name': self.site_name,
            'site_type': str(self.site_type),
            'site_type_id': self.site_type.pk,
            'barrier_status': str(self.barrier_status),
            'barrier_status_id': self.barrier_status.pk,
            'protocol': self.protocol,
            'assessed_by': self.assessed_by,
            'huc8_code': self.huc8_code,
            'huc8_name': self.huc8_name,
            'huc10_code': self.huc10_code,
            'huc10_name': self.huc10_name,
            'huc12_code': self.huc12_code,
            'huc12_name': self.huc12_name,
            'county': self.county,
            'ownership_type': str(self.ownership_type),
            'ownership_type_id': self.ownership_type.pk,
            'nhd_com_id': self.nhd_com_id,
            'nhd_com_meas': self.nhd_com_meas,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'state': self.state,
            'updated': self.updated.strftime('%Y-%m-%d'),
            'esu_coho': self.esu_coho,
            'esu_chinook': self.esu_chinook,
            'esu_steelhead': self.esu_steelhead,    # Steelhead have DPS, not ESU - fix by sharing label and value
            'upstream_miles': self.upstream_miles,  # this could use some number formatting
            'downstream_id': self.downstream_id,
            'downstream_barrier_count': self.downstream_barrier_count,
            'BIOS_link': "<a href=%s%s>link</a>" % (settings.BIOS_URL, self.pad_id),
            'estimated_cost': override_fields['estimated_cost'],
            'pre_passability': override_fields['pre_passability'],
            'post_passability': override_fields['post_passability'],
            'fixable': override_fields['fixable'],
            'action': override_fields['action'],
        }

    def __str__(self):
        return "%s: %s, %s" % (self.pad_id, self.site_name, self.stream_name)

    def save(self, *args, **kwargs):
        from django.contrib.gis.geos import Point
        self.geometry = Point(self.longitude, self.latitude,None,4326)
        super(Barrier, self).save(*args, **kwargs)

class BarrierCost(models.Model):
    # We want these to persist when new PAD imports are made, so we don't use FK to Barrier
    # However, we should delete any of these that no longer match a barrier after import
    pad_id = models.IntegerField(primary_key=True)
    cost = models.IntegerField(validators=[MinValueValidator(0.0)])

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

@register
class Project(Scenario):
    DS_TREATMENT_CHOICES = [
        ('adjust','Adjustable'),
        ('consider','Non-adjustable'),
        ('ignore','Excluded'),
    ]
    # OWNERSHIP_CHOICES = [(key, settings.OWNERSHIP_LOOKUP[key]) for key in settings.OWNERSHIP_LOOKUP.keys()]
    BUDGET_CHOICES = [
        ('budget','Fixed Budget'),
        ('batch','Ranged Budget')
    ]

    focus_region = models.ForeignKey(FocusArea)
    treat_downstream = models.CharField(max_length=30, default='consider', choices=DS_TREATMENT_CHOICES)

    # For pre-pass, post-pass, and cost estimates unique to this project, see:
    #   ScenarioBarrier (barrier specific for all three)
    #   ScenarioBarrierType (Change estimated cost or post-pass for a given type)
    #   ScenarioBarrierStatus (Change pre-pass for a given status)

    #TODO: sort this multiselect of unknown length out.
    ownership_input = models.TextField(blank=True, null=True, default=None)
    assign_cost = models.BooleanField(default=True,verbose_name="Assign Barrier Costs",help_text="Consider the unique cost of mitigating each barrier by $")
    budget_type = models.CharField(max_length=40, default='budget', verbose_name="Fixed Budget or Range")
    budget = models.IntegerField(null=True,blank=True,default=None,validators=[MinValueValidator(0)])
    min_budget = models.IntegerField(null=True,blank=True,default=None,validators=[MinValueValidator(0)])
    max_budget = models.IntegerField(null=True,blank=True,default=None,validators=[MinValueValidator(0)])
    batch_increment = models.IntegerField(null=True,blank=True,default=None,validators=[MinValueValidator(1)])

    target_area = gismodels.MultiPolygonField(srid=GEOMETRY_DB_SRID,
        null=True, blank=True, verbose_name="Target Area")
    objects = gismodels.GeoManager()

    # TODO: determine best way to store optipass results in scenario model
    # results = models.TextField(null=True,blank=True,default=None)

    class Options:
        verbose_name = 'Project'
        # icon_url = 'marco/img/multi.png'
        form = 'fishpass.forms.ProjectForm'
        form_template = 'scenarios/form.html'
        # form_template = 'fishpass/project_form.html'
        show_template = 'scenarios/show.html'

# outside of scenario model, between pad and user entry
class ScenarioBarrier(models.Model):
    ACTION_CHOICES = [
        ('consider', 'Consider'),
        ('include', 'Include in solution'),
        ('exclude', 'Exclude from solution')
    ]
    project = models.ForeignKey(Project)
    barrier = models.ForeignKey(Barrier)
    pre_pass = models.FloatField(null=True,blank=True,default=None,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],verbose_name="Pre-Passability")
    post_pass = models.FloatField(null=True,blank=True,default=None,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],verbose_name="Post-Passability")
    cost = models.FloatField(null=True,blank=True,default=None,verbose_name="Estimated cost to mitigate")
    action = models.CharField(max_length= 30, choices=ACTION_CHOICES, default='consider')

class ScenarioBarrierType(models.Model):
    project = models.ForeignKey(Project)
    barrier_type = models.ForeignKey(BarrierType)
    default_cost = models.FloatField(null=True,blank=True,verbose_name="Default Cost of Mitigation")
    default_post_passability = models.FloatField(null=True,blank=True,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],default=1.0,verbose_name='Post-passability')
    fixable = models.BooleanField(default=True)
    barrier_specific = models.BooleanField(default=False)

class ScenarioBarrierStatus(models.Model):
    project = models.ForeignKey(Project)
    barrier_status = models.ForeignKey(BarrierStatus)
    default_pre_passability = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],default=1.0, verbose_name='Pre-passability')

#class Default(models.Model):
# No. Barriers (no need)
# HUC size (?)
# Cost method (defaults)
# Barrier Status (own model)
# Weightings (outside of scope)
# Site Type (own model)
# Ownership (own model)
# PAD ESU/DPS (outside of scope)
# Species/ESU/DPS (outside of scope)
# HUC12/Name/Region (Focus Area + shapefiles)
# Code/Region (Focus Area)

#class DefaultCost(models.Model):
# PAD_ID/SiteType/Comments(1/2/3) (Barrier)
# Cost (BarrierCost)
