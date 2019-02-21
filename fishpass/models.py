from django.db import models
from django.conf import settings
from features.registry import register
from scenarios.models import Scenario#, PlanningUnit
from django.contrib.gis.db import models as gismodels
from django.core.validators import MaxValueValidator, MinValueValidator

GEOMETRY_DB_SRID = settings.GEOMETRY_DB_SRID

def purge_exports(uid='fishpass_project_'):
    import os, re
    for f in os.listdir(settings.CSV_REPORTS_DIR):
        if re.search(uid, f):
            os.remove(os.path.join(settings.CSV_REPORTS_DIR, f))

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

    def save(self, *args, **kwargs):
        super(BarrierType, self).save(*args, **kwargs)
        purge_exports()

    class Meta:
        verbose_name = 'Barrier Type'
        verbose_name_plural = 'Barrier Types'

class BarrierStatus(models.Model):
    name = models.CharField(max_length=90)
    default_pre_passability = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],default=1.0, verbose_name='Pre-passability')
    order = models.IntegerField(default=999)
    color = models.CharField(max_length=50, null=True, blank=True, default=None)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(BarrierStatus, self).save(*args, **kwargs)
        purge_exports()

    class Meta:
        verbose_name = 'Barrier Status'
        verbose_name_plural = 'Barrier Statuses'

class OwnershipType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    order = models.IntegerField(default=999)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(OwnershipType, self).save(*args, **kwargs)
        purge_exports()

    class Meta:
        verbose_name = 'Lookup - Ownership Type'
        verbose_name_plural = 'Lookup - Ownership Types'

class BlockedSpeciesType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Lookup - Blocked Species Type"
        verbose_name_plural = "Lookup - Blocked Species Types"

class TreatmentStatus(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Lookup - Treatment Status"
        verbose_name_plural = "Lookup - Treatment Statuses"

class Barrier(models.Model):
    # PAD_ID
    pad_id = models.IntegerField(primary_key=True,verbose_name="Barrier ID",help_text="The barrier ID as assigned in the PAD")
    # PassageID - ???
    passage_id = models.IntegerField(verbose_name="Passage ID",null=True,blank=True,default=None)
    # StreamName
    stream_name = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="Stream Name",help_text="The name of the waterbody obstructed by this barrier")
    # TributaryTo
    tributary_to = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="Tributary To",help_text="The waterbody that this obstructed waterbody flows into")
    # SiteName
    site_name = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="Site Name",help_text="Name of the site at which barrier is located, or name of the barrier itself")
    # SiteType
    site_type = models.ForeignKey(BarrierType,verbose_name="Barrier Type",)
    # BarStatus
    barrier_status = models.ForeignKey(BarrierStatus,verbose_name="Barrier Status")
    # Protocol
    protocol = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="Protocol",help_text="How the barrier was identified")
    # AssessedBy
    assessed_by = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name="Assessed By")
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
    state = models.CharField(max_length=5,null=True,blank=True,default=None)
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

    road = models.CharField(max_length=255, null=True, blank=True, default=None)                         # New in PAD - add to model!
    post_mile = models.FloatField(null=True, blank=True, default=None, verbose_name="Post Mile Marker")                # New in PAD - add to model!
    species_blocked = models.ForeignKey(BlockedSpeciesType, null=True, blank=True, default=None, verbose_name="Blocked Species Type")    # New in PAD - add to model!
    notes = models.TextField(null=True,blank=True,default=None)                       # New in PAD - add to model!
    #TrtStatus
    treatment_status = models.ForeignKey(TreatmentStatus,null=True,blank=True,default=None,verbose_name='Treatment Status')        # New in PAD - add to model!
    #TrtRecom
    treatment_recommendation = models.TextField(null=True,blank=True,default=None,verbose_name="Treatment Recommendation")                       # New in PAD - add to model!
    #Photo
    image_link = models.CharField(max_length=255,null=True, blank=True, default=None,verbose_name="Image Link")                  # New in PAD - add to model!

    # TODO: WHAT ARE THESE (types)?!
    accessible = models.TextField(null=True,blank=True,default=None,verbose_name='Accessible?')             # New in PAD - add to model!
    likely_exp = models.TextField(null=True,blank=True,default=None)

    # TODO: Overflow
    # NotSnappedReason
    # Trace_Status
    # Slope_Upstream_Avg
    # Flow_Aug_Upstream_Avg
    # Flow_Annual_Upstream_Avg
    # BFH
    # NorWeST_Mean_S1_93_11
    # NorWeST_Mean_S37_9311M
    overflow = models.TextField(null=True, blank=True, default=None, verbose_name="Additional Info")

    geometry = gismodels.PointField(null=True,blank=True,default=None,srid=settings.GEOMETRY_DB_SRID)

    def to_dict(self, project=None, downstream=False):
        # Calculate any project overrides (default by type and status)
        override_fields = {
            'estimated_cost': self.site_type.default_cost,
            'pre_passability': self.barrier_status.default_pre_passability,
            'post_passability': self.site_type.default_post_passability,
            # TODO: Perhaps: if not fixable, cost = NA, post_passability = 0, action = 'exclude'
            'fixable': self.site_type.fixable,
            'action': 'consider',
            'user_override': False,
        }
        # Consider project-level type and status overrides
        if project:
            override_type_list = ScenarioBarrierType.objects.filter(barrier_type=self.site_type,project=project)
            if override_type_list.count() > 0:
                override_type = override_type_list[0]
                if override_type.default_cost:
                    override_fields['estimated_cost'] = override_type.default_cost
                if override_type.default_post_passability:
                    override_fields['post_passability'] = override_type.default_post_passability
            override_status_list = ScenarioBarrierStatus.objects.filter(barrier_status=self.barrier_status,project=project)
            if override_status_list.count() > 0:
                override_status = override_status_list[0]
                if override_status.default_pre_passability:
                    override_fields['pre_passability'] = override_status.default_pre_passability
        # Consider Barrier Cost overrides
        barrier_costs = BarrierCost.objects.filter(pad_id=self.pad_id)
        if barrier_costs.count() > 0:
            if barrier_costs[0].site_type:
                override_fields['post_passability'] = barrier_costs[0].site_type.default_post_passability
                override_fields['estimated_cost'] = barrier_costs[0].site_type.default_cost
            if barrier_costs[0].cost:
                override_fields['estimated_cost'] = barrier_costs[0].cost
            if barrier_costs[0].barrier_status:
                override_fields['pre_passability'] = barrier_costs[0].barrier_status.default_pre_passability
        # Consider Project-Specific Barrier overrides
        if project:
            override_barrier_list = ScenarioBarrier.objects.filter(barrier=self,project=project)
            if override_barrier_list.count() > 0:
                override_barrier = override_barrier_list[0]
                override_fields['user_override'] = True
                if override_barrier.pre_pass:
                    override_fields['pre_passability'] = override_barrier.pre_pass
                if override_barrier.post_pass:
                    override_fields['post_passability'] = override_barrier.post_pass
                if override_barrier.cost:
                    override_fields['estimated_cost'] = override_barrier.cost
                if override_barrier.action:
                    override_fields['action'] = override_barrier.action

        if self.updated:
            updated = self.updated.strftime('%Y-%m-%d')
        else:
            updated = None

        if self.species_blocked:
            species_blocked = str(self.species_blocked)
        else:
            species_blocked = None

        if self.treatment_status:
            treatment_status = str(self.treatment_status)
        else:
            treatment_status = None

        if self.image_link:
            image_link = str(self.image_link)
        else:
            image_link = None

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
            'updated': updated,
            'esu_coho': self.esu_coho,
            'esu_chinook': self.esu_chinook,
            'esu_steelhead': self.esu_steelhead,    # Steelhead have DPS, not ESU - fix by sharing label and value
            'upstream_miles': self.upstream_miles,  # this could use some number formatting
            'downstream_id': self.downstream_id,
            'downstream_barrier_count': self.downstream_barrier_count,
            'BIOS_link': '<a href=%s%s target="_blank">link</a>' % (settings.BIOS_URL, self.pad_id),
            'estimated_cost': override_fields['estimated_cost'],
            'pre_passability': override_fields['pre_passability'],
            'post_passability': override_fields['post_passability'],
            'fixable': override_fields['fixable'],
            'action': override_fields['action'],
            'user_override': override_fields['user_override'],
            'downstream_only': downstream,
            'road' : self.road,
            'post_mile': self.post_mile,
            'species_blocked': species_blocked,
            'notes': self.notes,
            'treatment_status': treatment_status,
            'treatment_recommendation': self.treatment_recommendation,
            'image_link': image_link,
            'accessible': self.accessible,
            'likely_exp': self.likely_exp,
        }

    def __str__(self):
        return "%s: %s, %s" % (self.pad_id, self.site_name, self.stream_name)

    def save(self, *args, **kwargs):
        from django.contrib.gis.geos import Point
        self.geometry = Point(self.longitude, self.latitude,None,4326)
        super(Barrier, self).save(*args, **kwargs)
        purge_exports()

    class Meta:
        verbose_name = 'Barrier'
        verbose_name_plural = 'Barriers'

class BarrierCost(models.Model):
    # We want these to persist when new PAD imports are made, so we don't use FK to Barrier
    pad_id = models.IntegerField(primary_key=True)
    cost = models.IntegerField(validators=[MinValueValidator(0.0)],null=True,blank=True,default=None)
    site_type = models.ForeignKey(BarrierType,null=True,blank=True,default=None,verbose_name="Barrier Type")
    barrier_status = models.ForeignKey(BarrierStatus,null=True,blank=True,default=None,verbose_name="Barrier Status")
    comment = models.TextField(null=True,blank=True,default=None,verbose_name="Comments")

    def __str__(self):
        try:
            barrier = Barrier.objects.get(pad_id=self.pad_id)
            barrier_name = str(barrier)
        except:
            barrier_name = str(self.pad_id)
            pass
        return "%s Costs" % barrier_name

    def save(self, *args, **kwargs):
        super(BarrierCost, self).save(*args, **kwargs)
        purge_exports()

    class Meta:
        verbose_name = 'Barrier Specific Override'
        verbose_name_plural = 'Barrier Specific Overrides'

class FocusArea(models.Model):
    UNIT_TYPE_CHOICES = []
    for type in settings.FOCUS_AREA_TYPES.keys():
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

    class Meta:
        verbose_name = 'Lookup - Focus Area'
        verbose_name_plural = 'Lookup - Focus Areas'

@register
class Project(Scenario):
    from features.managers import ShareableGeoManager
    # OWNERSHIP_CHOICES = [(key, settings.OWNERSHIP_LOOKUP[key]) for key in settings.OWNERSHIP_LOOKUP.keys()]
    BUDGET_CHOICES = [
        ('budget','Fixed Budget'),
        ('batch','Ranged Budget')
    ]

    # RDH: Is focus region going to be a multipolygon clone of the FocusAreas selected?
    # focus_region = models.ForeignKey(FocusArea)
    # This sounds like the same thing as how focus_region is used above... RDH likes how this one will be cleaned up
    #   with any changed/deleted Project records.
    # target_area = gismodels.MultiPolygonField(srid=GEOMETRY_DB_SRID,
    # null=True, blank=True, verbose_name="Target Area")

    UNIT_TYPE_CHOICES = []
    for type in settings.FOCUS_AREA_TYPES.keys():
        UNIT_TYPE_CHOICES.append((type, type))

    spatial_organization = models.CharField(max_length=50, null=True, blank=True, default=None, choices=UNIT_TYPE_CHOICES)

    target_area = models.TextField(blank=True,null=True,default=None,help_text="list of FocusArea IDs that make up the target area geometry")

    treat_downstream = models.CharField(max_length=30, default='consider', choices=settings.DS_TREATMENT_CHOICES)

    try:
        checkbox_default = str([str(x.id) for x in OwnershipType.objects.all()])
    except Exception as e:
        checkbox_default = None
    ownership_input = models.BooleanField(default=False,verbose_name="Select ownership types")
    ownership_input_checkboxes = models.TextField(blank=True, null=True, default=checkbox_default)
    assign_cost = models.BooleanField(default=True,verbose_name="Assign Barrier Costs",help_text="Consider the unique cost of mitigating each barrier by $")
    budget_type = models.CharField(max_length=40, default='budget', choices=BUDGET_CHOICES, verbose_name="Fixed Budget or Range")
    budget = models.IntegerField(null=True,blank=True,default=0,validators=[MinValueValidator(0)])
    budget_min = models.IntegerField(null=True,blank=True,default=0,validators=[MinValueValidator(0)])
    budget_max = models.IntegerField(null=True,blank=True,default=100000,validators=[MinValueValidator(0)])
    batch_increment = models.IntegerField(null=True,blank=True,default=10000,validators=[MinValueValidator(1)])

    objects = ShareableGeoManager()

    # See ProjectReport and ProjectReportBarrier
    # results = models.TextField(null=True,blank=True,default=None)

    def __str__(self):
        return self.name

    def run_filters(self, query):
        from fishpass.views import run_filter_query

        filters = {}

        if self.ownership_input:
            ownership_keys = []
            filters['ownership_input'] = 'true'
            filters['ownership_input_checkboxes'] = 'true'
            for key in eval(self.ownership_input_checkboxes):
                filters['ownership_input_checkboxes_%d' % int(key)] = 'true'

        focus_ids = []
        if self.target_area and len(self.target_area) > 0:
            filters['target_area'] = 'true'
            filters['target_area_input'] = self.target_area

        filters['treat_downstream'] = 'true'
        filters['treat_downstream_input'] = self.treat_downstream

        (query, notes) = run_filter_query(filters)
        return query

    def run(self, result=None):
        # if self.focus_area_input:
        #     result = Barrier.objects.filter(geometry__intersects=self.focus_area_input.geometry)
        # else:
        result = Barrier.objects.all()
        if result.count() > 0:
            # return super(type(self), self).run(result)
            result = self.run_filters(result)
            self.active = True
            if result.count() > 0:
                self.satisfied = True
            else:
                self.satisfied = False
        return result

    def to_dict(self):
        return {
            'spatial_organization': self.spatial_organization,
            'target_area': self.target_area,
            'treat_downstream': self.treat_downstream,
            'ownership_input': self.ownership_input,
            'ownership_input_checkboxes': self.ownership_input_checkboxes,
            'assign_cost': self.assign_cost,
            'budget_type': self.budget_type,
            'budget': self.budget,
            'budget_min': self.budget_min,
            'budget_max': self.budget_max,
            'batch_increment': self.batch_increment,
            # TODO:?
            'report': {}
        }

    @property
    def has_report(self):
        if ProjectReport.objects.filter(project=self).count() > 0:
            return True
        return False

    def save(self, *args, **kwargs):
        from fishpass import celery
        from fishpass.views import generate_report_csv
        from django.core.cache import cache
        super(Project, self).save(*args, **kwargs)
        for report_type in ['all', 'filtered']:
            cache_key = "%s_%s_report_task_id" % (self.uid, report_type)
            try:
                celery_task = celery.run_view.delay('fishpass', 'generate_report_csv', self.uid, report_type)
                cache.set(cache_key, celery_task.task_id, 60*60*24*7)
            except Exception as e:
                generate_report_csv(self.uid, report_type)
                pass

    class Options:
        verbose_name = 'Project'
        # icon_url = 'marco/img/multi.png'
        form = 'fishpass.forms.ProjectForm'
        form_template = 'fishpass/scenarios/fishpass_form.html'
        # form_template = 'fishpass/project_form.html'
        # show_template = 'scenarios/show.html'
        show_template = 'fishpass/demo.html'

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

class ProjectReport(models.Model):
    project = models.ForeignKey(Project)
    budget = models.IntegerField(default=0)
    status = models.CharField(max_length=10, default='')
    optgap = models.FloatField(verbose_name='percent optimality gap',default=0.0)
    ptnl_habitat = models.FloatField(verbose_name='potential habitat',default=0.0)
    netgain = models.FloatField(verbose_name='net gain',default=0.0)

    def uid(self):
        return "%s_report" % self.project.uid

    def __str__(self):
        return "%s Report" % str(self.project)

    def cost(self):
        barriers = ProjectReportBarrier.objects.filter(project_report=self, action=1)
        cost=0
        for barrier in barriers:
            if barrier.estimated_cost:
                cost += barrier.estimated_cost
        return cost

    def action_barriers_list(self):
        return ProjectReportBarrier.objects.filter(project_report=self, action=1).order_by('barrier_id')

    def action_barriers_list(self, action_only=False):
        if action_only:
            return []
        else:
            return ProjectReportBarrier.objects.filter(project_report=self, action=0).order_by('barrier_id')

    def barriers_list(self, action_only=False):
        from django.core.cache import cache
        if action_only:
            # cache_key = "%s_%s_barriers_list_action_only" % (self.uid(), str(self.budget))
            barriers = ProjectReportBarrier.objects.filter(project_report=self, action=1).order_by('barrier_id')
        else:
            barriers = ProjectReportBarrier.objects.filter(project_report=self).order_by('barrier_id')
            # cache_key = "%s_%s_barriers_list" % (self.uid(), str(self.budget))
        # barrier_list = cache.get(cache_key)
        # if not barrier_list:
            # barrier_list = [x.barrier_id for x in barriers]
        return barriers

    def barriers_dict(self, action_only=False):
        from django.core.cache import cache
        if action_only:
            cache_key = "%s_%s_barriers_action_only" % (self.uid(), str(self.budget))
        else:
            cache_key = "%s_%s_barriers" % (self.uid(), str(self.budget))
        print("CACHE KEY: %s" % cache_key)
        barrier_dict = cache.get(cache_key)
        if not barrier_dict:
            if action_only:
                barriers = ProjectReportBarrier.objects.filter(project_report=self, action=1).order_by('barrier_id')
            else:
                barriers = ProjectReportBarrier.objects.filter(project_report=self).order_by('barrier_id')
            barrier_dict = {}
            for barrier in barriers:
                barrier_dict[barrier.barrier_id] = barrier.to_dict()

            # Cache for 1 week, will be reset if layer data changes
            cache.set(cache_key, barrier_dict, 60*60*24*7)
        return barrier_dict

    def to_dict(self):
        total_barriers = ProjectReportBarrier.objects.filter(project_report=self)
        action_barriers = total_barriers.filter(action=1)
        cost = 0
        for action_barrier in action_barriers:
            bar_dict = action_barrier.to_dict()
            try:
                cost += int(bar_dict['Estimated Cost'].replace(',','').replace('$',''))
            except ValueError as e:
                # Value is 'NA' - nothing to add to cost.
                pass

        if self.project.assign_cost:
            assign_cost = "$%s" % "{:,}".format(round(self.project.assign_cost))
        else:
            assign_cost = None

        if self.budget:
            budget = "$%s" % "{:,}".format(self.budget)
        else:
            budget = None

        budget_min = None
        budget_max = None
        try:
            if self.budget_min:
                budget_min = "$%s" % "{:,}".format(round(self.project.budget_min))

            if self.budget_max:
                budget_max = "$%s" % "{:,}".format(round(self.project.budget_max))
        except AttributeError as e:
            pass

        if self.ptnl_habitat:
            ptnl_habitat = "%s mi" % "{:,}".format(round(self.ptnl_habitat,2))
        else:
            ptnl_habitat = None

        if self.netgain:
            netgain = "%s mi" % "{:,}".format(round(self.netgain,2))
        else:
            netgain = None

        out_dict = {
            'project': str(self.project),
            'assign_cost': assign_cost,
            'budget_type': self.project.budget_type,
            'barrier_count': total_barriers.count(),
            'action_count': action_barriers.count(),
            'cost': "$%s" % "{:,}".format(round(cost)),
            'budget': budget,
            'budget_int': self.budget,
            'budget_min': budget_min,
            'budget_max': budget_max,
            'ptnl_habitat': ptnl_habitat,
            'netgain': netgain,
        }

        return out_dict

    def save(self, *args, **kwargs):
        from django.core.cache import cache
        cache.delete("%s_%s_barriers_action_only" % (self.uid(), str(self.budget)))
        cache.delete("%s_%s_barriers" % (self.uid(), str(self.budget)))
        cache.delete("get_report_%s_action_only" % self.uid())
        super(ProjectReport, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Project Report'
        verbose_name_plural = 'Project Reports'

class ProjectReportBarrier(models.Model):
    project_report = models.ForeignKey(ProjectReport)
    barrier_id = models.CharField(max_length=50)
    action = models.IntegerField(default=0)
    estimated_cost = models.IntegerField(null=True,blank=True,default=None)
    pre_passability = models.FloatField(default=0.0)
    post_passability = models.FloatField(default=0.0)

    def get_absolute_passability(self, bar_record=False):
        if not bar_record:
            bar_record = Barrier.objects.get(pk=self.barrier_id)
        barrier_dict = bar_record.to_dict(self.project_report.project)
        if bar_record.downstream_barrier_count > 0:
            ds_report_barrier = ProjectReportBarrier.objects.get(barrier_id=bar_record.downstream_id, project_report=self.project_report)
            ds_passability = ds_report_barrier.get_absolute_passability()
        else:
            ds_passability = 1
        if self.action == 1:
            passability = barrier_dict['post_passability']
        else:
            passability = barrier_dict['pre_passability']
        return passability * ds_passability

    def potential_habitat(self, bar_record=False):
        if not bar_record:
            bar_record = Barrier.objects.get(pk=self.barrier_id)
        barrier_dict = bar_record.to_dict(self.project_report.project)
        if self.project_report.project.treat_downstream == 'ignore':
            if self.action == 1:
                return bar_record.upstream_miles * barrier_dict['post_passability']
            else:
                return bar_record.upstream_miles * barrier_dict['pre_passability']
        else:
            absolute_passability = self.get_absolute_passability(bar_record)
            return bar_record.upstream_miles * absolute_passability

    def to_dict(self):
        from django.core.cache import cache
        cache_key = "project_barrier_%s" % self.pk
        report_dict = cache.get(cache_key)
        if not report_dict:
            from collections import OrderedDict
            bar_record = Barrier.objects.get(pk=self.barrier_id)
            report_dict = OrderedDict()
            report_dict['Site Name'] = bar_record.site_name
            report_dict['PAD ID'] = self.barrier_id
            report_dict['View in BIOS'] = '<a href=%s%s target="_blank">link</a>' % (settings.BIOS_URL, self.barrier_id)
            if self.action == 1:
                report_dict['Action'] = 'Treat'
            else:
                report_dict['Action'] = 'Do not treat'
            report_dict['Potential Habitat'] = "%s mi" % round(self.potential_habitat(bar_record), 2)
            if self.estimated_cost:
                report_dict['Estimated Cost'] = "$%s" % "{:,}".format(round(self.estimated_cost))
            else:
                report_dict['Estimated Cost'] = "NA"
            report_dict['Barriers Downstream'] = bar_record.downstream_barrier_count
            report_dict['Site Type'] = bar_record.site_type
            report_dict['Stream Name'] = bar_record.stream_name
            report_dict['Tributary To'] = bar_record.tributary_to
            # Get watershed name:
            ws_name_field = settings.FOCUS_AREA_TYPE_NAME_LOOKUP[self.project_report.project.spatial_organization]
            report_dict['Watershed'] = getattr(bar_record, ws_name_field)
            report_dict['County'] = bar_record.county
            if bar_record.image_link and len(bar_record.image_link) > 0:
                report_dict['Image'] = '<img src="' + bar_record.image_link + '" class="barrier-image">'
            else:
                report_dict['Image'] = ""
            report_dict['Coordinates'] = "%s, %s" % (bar_record.latitude, bar_record.longitude)
            cache.set(cache_key, report_dict, 60*60*24*7)
        return report_dict

    class Meta:
        verbose_name = 'Project Report Barrier'
        verbose_name_plural = 'Project Report Barriers'

    def save(self, *args, **kwargs):
        from django.core.cache import cache
        cache.delete("project_barrier_%s" % self.pk)
        super(ProjectReportBarrier, self).save(*args, **kwargs)

# outside of scenario model, between pad and user entry
class ScenarioBarrier(models.Model):
    ACTION_CHOICES = [
        ('consider', 'Consider for solution'),
        ('include', 'Include in solution'),
        ('exclude', 'Exclude from solution')
    ]
    project = models.ForeignKey(Project)
    barrier = models.ForeignKey(Barrier)
    pre_pass = models.FloatField(null=True,blank=True,default=None,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],verbose_name="Pre-Passability")
    post_pass = models.FloatField(null=True,blank=True,default=None,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],verbose_name="Post-Passability")
    cost = models.FloatField(null=True,blank=True,default=None,verbose_name="Estimated cost to mitigate")
    action = models.CharField(max_length= 30, choices=ACTION_CHOICES, default='consider')

    class Meta:
        verbose_name = 'Project-Specific Barrier Setting'
        verbose_name_plural = 'Project-Specific Barrier Settings'

    def save(self, *args, **kwargs):
        super(ScenarioBarrier, self).save(*args, **kwargs)
        purge_exports(self.project.uid)

class ScenarioBarrierType(models.Model):
    project = models.ForeignKey(Project)
    barrier_type = models.ForeignKey(BarrierType)
    default_cost = models.FloatField(null=True,blank=True,default=None,verbose_name="Default Cost of Mitigation")
    default_post_passability = models.FloatField(null=True,blank=True,default=None,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],verbose_name='Post-passability')

    class Meta:
        verbose_name = 'Project-Specific Barrier Type Setting'
        verbose_name_plural = 'Project-Specific Barrier Type Settings'

    def save(self, *args, **kwargs):
        super(ScenarioBarrierType, self).save(*args, **kwargs)
        purge_exports(self.project.uid)

class ScenarioBarrierStatus(models.Model):
    project = models.ForeignKey(Project)
    barrier_status = models.ForeignKey(BarrierStatus)
    default_pre_passability = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],default=1.0, verbose_name='Pre-passability')

    class Meta:
        verbose_name = 'Project-Specific Barrier Status Setting'
        verbose_name_plural = 'Project-Specific Barrier Status Settings'

    def save(self, *args, **kwargs):
        super(ScenarioBarrierStatus, self).save(*args, **kwargs)
        purge_exports(self.project.uid)
