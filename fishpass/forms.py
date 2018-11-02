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
#     project = forms.ChoiceField(choices=)
#     barrier = models.ForeignKey(Barrier)
#     pre_pass = models.FloatField(null=True,blank=True,default=None,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],verbose_name="Pre-Passability")
#     post_pass = models.FloatField(null=True,blank=True,default=None,validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],verbose_name="Post-Passability")
#     cost = models.FloatField(null=True,blank=True,default=None,verbose_name="Estimated cost to mitigate")
#     action
#
#
#     class Meta(FeatureForm.Meta):
#         model = ScenarioBarrier

class ProjectBarrierStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from fishpass.models import BarrierStatus
        barrier_statuses = BarrierStatus.objects.all()
        # project id is sent along with ajax request
        for status in barrier_statuses.order_by('order'):
            barrier_status_field_name = status.id
            # project_barrier_status_field_name = status.id
            try:
                self[barrier_status_field_name] = barrier_status_field_name
            except IndexError:
                self[barrier_status_field_name] = ''
            self.fields[barrier_status_field_name] = forms.CharField(required=False, disabled=True, verbose_name="Barrier Status", value=status.default_pre_passability)

            self.fields['project_barrier_status'] = forms.CharField(required=False, verbose_name="Project Barrier Status", value=status.default_pre_passability)

        # reference https://www.caktusgroup.com/blog/2018/05/07/creating-dynamic-forms-django/
        # 1. create field name for each status using id
        # 2. create field
        # 3. populate field
        # barrier status as field that is disabled=true. prepopulated with

        # create input field name with name = status id
        # create input field
        # populate value with current default for barrier.default_pre_passability
    def clean():
        project_barrier_statuses = set()
        for status in self:
            barrier_status_field_name = self.cleaned_data[status.barrier_status_field_name]
            if barrier_status_field_name in project_barrier_statuses:
               self.add_error(barrier_status_field_name, 'Duplicate')
            else:
               project_barrier_statuses.add(barrier_status_field_name)
        self.cleaned_data["project_barrier_statuses"] = project_barrier_statuses

    def save(self):
        from fishpass.models import ScenarioBarrierStatus
        status_form = self.instance
        status_form.project_barrier_statuses.all().delete()
        for status in self.cleaned_data["project_barrier_statuses"]:
           ScenarioBarrierStatus.objects.create(
               project=project,
               barrier_status=status,
               default_pre_passability=status.project_barrier_status,
           )

class UploadPADForm(forms.Form):
    file = forms.FileField()

class UploadBarrierCostForm(forms.Form):
    file = forms.FileField()
