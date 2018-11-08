from fishpass.models import *
from features.forms import FeatureForm, SpatialFeatureForm
from scenarios.forms import ScenarioForm
from django import forms
from django.conf import settings
from django.forms.widgets import *
from analysistools.widgets import SliderWidget, DualSliderWidget
from django.forms import ModelMultipleChoiceField, CheckboxSelectMultiple
# from scenarios.widgets import AdminFileWidget, SliderWidgetWithTooltip, DualSliderWidgetWithTooltip, CheckboxSelectMultipleWithTooltip, CheckboxSelectMultipleWithObjTooltip


class HiddenScenarioBooleanField(forms.BooleanField):
    # initial=False,
    widget=CheckboxInput(
        attrs={
            'class': 'parameters hidden_checkbox'
        }
    )

class ProjectForm(ScenarioForm):
    from fishpass.models import FocusArea, OwnershipType

    # TODO: Select FocusArea Layer
    UNIT_TYPE_CHOICES = []
    for type in settings.FOCUS_AREA_TYPES:
        UNIT_TYPE_CHOICES.append((type, type))

    spatial_organization = forms.ChoiceField(
        choices = UNIT_TYPE_CHOICES,
        label="spatial organization",
        # help_text="",
        required=True,
        initial='County'
    )

    # focus_region = HiddenScenarioBooleanField(
    #     label="Filter By Boundary",
    #     help_text="This should be true: ALWAYS",
    #     initial=True,
    #     required=False,
    # )
    #
    # target_area = HiddenScenarioBooleanField(
    #     label="Filter By Boundary",
    #     help_text="This should be true: ALWAYS",
    #     initial=True,
    #     required=True,
    # )

    target_area = forms.CharField(
        widget=forms.Textarea,
        label="Target Area",
        help_text="This should be invisible. Stringified GeoJSON Multiselection of FocusAreas",
        required=False,
    )

    treat_downstream = forms.ChoiceField(
        choices = settings.DS_TREATMENT_CHOICES,
        label="Downstream Treatment",
        help_text="Should downstream mitigation be an option ('adjustable'), should downstream passability be considered in optimization ('non-adjustable'), or completely ignored ('excluded')?",
        # required=True,
        required=False,
        initial='consider',
    )

    # TODO: pre-pass/post-pass/cost-estimates:
    #     ScenarioBarrierType
    #     ScenarioBarrierStatus
    #     scenarioBarrier
    # This is likely best handled inside of a custom forms.html

    ownership_input = HiddenScenarioBooleanField(
        label="Filter By Ownership",
        # help_text="This should be true: ALWAYS",
        initial=False,
        required=False,
    )

    ownership_input_options = ((x, settings.OWNERSHIP_LOOKUP[x]) for x in settings.OWNERSHIP_LOOKUP.keys())
    initial_ownership = list(set([str(x.id) for x in OwnershipType.objects.all()] + [x for x in settings.OWNERSHIP_LOOKUP.keys()]))

    ownership_input_checkboxes = forms.MultipleChoiceField(
        # required=True,
        required=False,
        choices=ownership_input_options,
        widget=forms.CheckboxSelectMultiple(),
        initial=initial_ownership,
        label="OwnershipT Type",
        help_text="Uncheck any ownership type that you don't wish to consider for mitigation",
    )

    assign_cost = forms.BooleanField(
        label="Use Estimated Costs",
        help_text="Uncheck to treat the effort of mitigating each barrier as equal",
        required = False,
        initial=True
    )

    # TODO: Allow users to edit estimated costs by Barrier Type

    budget_type = forms.ChoiceField(
        choices = (('budget', 'Fixed Budget'),('batch', 'Ranged Budget')),
        label="Budget Type",
        help_text="'Fixed Budget' for a known buget, 'Ranged Budget' to find the best ROI btween a min/max budget",
        required=True,
        initial='budget'
    )

    budget = forms.IntegerField(
        label='Budget ($)',
        initial=0,
        min_value=0,
    )

    budget_min = forms.IntegerField(
        required=False,
        initial=100000,
        widget=forms.TextInput(
            attrs={
                'class': 'slidervalue readonly-value',
                'pre_text': 'from',
                'readonly': 'readonly',
                'post_text': '$',
            }
        )
    )

    budget_max = forms.IntegerField(
        required=False,
        initial=1000000,
        widget=forms.TextInput(
            attrs={
                'class': 'slidervalue readonly-value',
                'pre_text': 'to',
                'readonly': 'readonly',
                'post_text': '$',
            }
        )
    )

    budget_input = forms.IntegerField(
        widget=DualSliderWidget(
            'budget_min',
            'budget_max',
            min=0,
            max=50000000,
            step=1000           #This doesn't work at all for non-assigned costs. Do we need to make 2 of these?
        )
    )

    batch_increment = forms.IntegerField(
        label='Increment',
        initial=10000,
        min_value=1,            # has to be 1 for scenarios where estimated cost is not considered
    )

    def get_step_0_fields(self):
        names = [
            # (bool_field, min, max, field, [checkboxes])
            # ('target_area', None, None, 'target_area_input'),
            (None, None, None, 'spatial_organization'),
            (None, None, None, 'target_area'),
            (None, None, None, 'treat_downstream'),

        ]
        return self._get_fields(names)

    def get_step_1_fields(self):
        names = [
            ('ownership_input', None, None, None, 'ownership_input_checkboxes'),
        ]
        return self._get_fields(names)

    def get_step_2_fields(self):
        names = [
            (None, None, None, 'assign_cost'),
            (None, None, None, 'budget_type'),
            (None, None, None, 'budget'),
            (None, 'budget_min', 'budget_max', 'budget_input'),
            (None, None, None, 'batch_increment'),
        ]
        return self._get_fields(names)

    def get_steps(self):
        #TODO: fill steps_list with your get_step_fields functions
        steps_list = (self.get_step_0_fields(),self.get_step_1_fields(),self.get_step_2_fields(),)
        return_list = []
        default_instructions = 'Select criteria to filter your results'
        for step in steps_list:
            if type(step) == dict:
                if not 'fields' in step.keys():
                    step['fields'] = []
                if not 'instructions' in step.keys():
                    step['instructions'] = default_instructions
                return_list.append(step)
            else:
                step_dict = {'instructions': default_instructions }
                if type(step) == list:
                    step_dict['fields'] = step
                else:
                    step_dict['fields'] = []
                return_list.append(step_dict)
        return return_list

    def clean_focus_area_input(self):
        return FocusArea.objects.get(pk=self.cleaned_data['focus_area_input'])

    def is_valid(self, *args, **kwargs):
        if len(self.errors.keys()) == 1 and 'ownership_input_checkboxes' in self.errors.keys() and len(self.errors['ownership_input_checkboxes']) == 1 and 'is not one of the available choices.' in self.errors['ownership_input_checkboxes'][0]:
            del self._errors['ownership_input_checkboxes']
        return super(ScenarioForm, self).is_valid()

    def clean(self):
        super(FeatureForm, self).clean()
        try:
            if 'ownership_input_checkboxes' not in self.cleaned_data.keys() and self.cleaned_data['ownership_input'] == True:
                checkdata = self.data.getlist('ownership_input_checkboxes')
                checklist = False
                for box in checkdata:
                    if not box == 'False':
                        checklist = True
                        self.cleaned_data['ownership_input_checkboxes'] = str([str(x) for x in box.split(',')])
                if not checklist:
                    self.data.__delitem__('ownership_input_checkboxes')
        except Exception as e:
            print(e)
            pass
        return self.cleaned_data

    # def save(self, commit=True):
    #     # remove fields that are not on current model (FocusArea.unit_type)
    #     inst = super(ProjectForm, self).save(commit=True)
    #     # Run OptiPass
    #     from fishpass.views import optipass
    #     inst = optipass(inst)
    #     inst.save()
    #     return inst


    class Meta(ScenarioForm.Meta):
        model = Project
        exclude = list(ScenarioForm.Meta.exclude)
        for f in model.output_fields():
            exclude.append(f.attname)
        widgets = {}

# class ProjectBarrierForm(forms.Form):
    # project = forms.ChoiceField(choices=)
    # barrier = models.ForeignKey(Barrier)
    # pre_pass = models.FloatField(null=True,blank=True,default=None,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],verbose_name="Pre-Passability")
    # post_pass = models.FloatField(null=True,blank=True,default=None,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],verbose_name="Post-Passability")
    # cost = models.FloatField(null=True,blank=True,default=None,verbose_name="Estimated cost to mitigate")
    # action
    #
    # class Meta(FeatureForm.Meta):
    #     model = ScenarioBarrier



class ProjectBarrierTypeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from fishpass.models import BarrierType, ScenarioBarrierType
        barrier_types = BarrierType.objects.all()
        for type in barrier_types.order_by('order'):

            # type name field (noneditable)
            # import ipdb; ipdb.set_trace()
            type_name = '%s_%s' % (id,type,)
            self.fields[type_name] = forms.CharField(required=False, disabled=True, label='')
            try:
                self.initial[type_name] = type
            except IndexError:
                self.initial[type_name] = ''
            # barrier = models.ForeignKey(BarrierType)
            # type default cost field name and field (editable)
            cost = models.FloatField(null=True,blank=True,default=None,verbose_name="Estimated cost to mitigate")
            # type default post passability field name and field (editable)
            post_pass = models.FloatField(null=True,blank=True,default=None,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],verbose_name="Post-Passability")

    class Meta(FeatureForm.Meta):
        model = ScenarioBarrierType

class PrePassField(forms.FloatField):
    def validate(self, value):
        # For some reason this validates on 'GET' and does not recognize initial values.
        from fishpass.models import Project, BarrierStatus, ScenarioBarrierStatus
        if value is None:
            project = Project.objects.get(pk=self.widget.attrs['project'])
            status = BarrierStatus.objects.get(pk=self.widget.attrs['status'])
            try:
                default_value = ScenarioBarrierStatus.objects.get(project=project, barrier_status=status).default_pre_passability
            except:
                default_value = BarrierStatus.objects.get(pk=status).default_pre_passability
            self.initial = default_value
            value = default_value
        # Use the parent's handling of required fields, etc.
        super(PrePassField, self).validate(value)

class ProjectBarrierStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        from fishpass.models import BarrierStatus, ScenarioBarrierStatus
        # Get the project
        project = kwargs.pop('project')
        # Call the default init process
        super().__init__(*args, **kwargs)

        # Get the default BarrierStatus objects
        barrier_statuses = BarrierStatus.objects.all()

        # Step through all barrier status instances
        for status in barrier_statuses.order_by('order'):
            # # Create name field for each instance
            # barrier_status_field_name = 'status_%s' % (status.name,)
            # # self.fields[barrier_status_field_name] = forms.CharField(required=False, disabled=True, label='')
            # self.fields[barrier_status_field_name] = forms.CharField(disabled=True, label='')
            # self.initial[barrier_status_field_name] = status.name

            # create pre-pass field for each instance
            barrier_status_prepass_field_name = "status_type_%s" % status.name
            self.fields[barrier_status_prepass_field_name] = PrePassField(
                label=status.name,
                widget=NumberInput(
                    attrs={
                        'id': 'id_%s' % barrier_status_prepass_field_name,
                        'step': "0.1",  # should this be 0.05?
                        'max': "1.0",
                        'min': "0.0",
                        "status": status.pk,
                        "project": project.pk,
                    }
                )
            )
            if project:
                proj_status, created = ScenarioBarrierStatus.objects.get_or_create(project=project, barrier_status=status)
                if created:
                    proj_status.default_pre_passability = status.default_pre_passability
                    proj_status.save()
                self.initial[barrier_status_prepass_field_name] = proj_status.default_pre_passability
                self.fields[barrier_status_prepass_field_name].initial = proj_status.default_pre_passability
            else:
                self.initial[barrier_status_prepass_field_name] = status.default_pre_passability
                self.fields[barrier_status_prepass_field_name].initial = status.default_pre_passability

    def clean(self):
        cleaned_data = super(ProjectBarrierStatusForm, self).clean()
        for key, value in cleaned_data.items():
            if value is None and key in self.initial:
                cleaned_data[key] = self.initial[key]
        self.cleaned_data = cleaned_data
        self.data = cleaned_data
        return cleaned_data

    def save(self, project):
        from fishpass.models import ScenarioBarrierStatus, BarrierStatus
        for field_name in self.fields:
            field = self.fields[field_name]
            status = BarrierStatus.objects.get(pk=field.widget.attrs['status'])
            proj_status, created = ScenarioBarrierStatus.objects.get_or_create(project=project, barrier_status=status)
            proj_status.default_pre_passability = self.cleaned_data[field_name]
            proj_status.save()

class UploadPADForm(forms.Form):
    file = forms.FileField()

class UploadBarrierCostForm(forms.Form):
    file = forms.FileField()
