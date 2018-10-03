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
    from fishpass.models import FocusArea

    # TODO: Select FocusArea Layer

    target_area = HiddenScenarioBooleanField(
        label="Filter By Boundary",
        help_text="This should be true: ALWAYS",
        initial=True
    )

    target_area_input = forms.CharField(
        widget=forms.Textarea,
        label="Target Area",
        help_text="This should be invisible. Stringified GeoJSON Multiselection of FocusAreas",
        required=False,
    )

    treat_downstream = forms.ChoiceField(
        choices = settings.DS_TREATMENT_CHOICES,
        label="Downstream Treatment",
        help_text="Should downstream mitigation be an option ('adjustable'), should downstream passability be considered in optimization ('non-adjustable'), or completely ignored ('excluded')?",
        required=True,
        initial='consider'
    )

    # TODO: pre-pass/post-pass/cost-estimates:
    #     ScenarioBarrierType
    #     ScenarioBarrierStatus
    #     scenarioBarrier
    # This is likely best handled inside of a custom forms.html

    ownership_input = HiddenScenarioBooleanField(
        label="Filter By Ownership",
        # help_text="This should be true: ALWAYS",
        initial=False
    )

    ownership_input_options = ((x, settings.OWNERSHIP_LOOKUP[x]) for x in settings.OWNERSHIP_LOOKUP.keys())
    initial_ownership = (x for x in settings.OWNERSHIP_LOOKUP.keys())
    ownership_input_checkboxes = forms.MultipleChoiceField(
        required=True,
        choices=ownership_input_options,
        widget=forms.CheckboxSelectMultiple(),
        initial=initial_ownership,
        label="OwnershipT Type",
        help_text="Uncheck any ownership type that you don't wish to consider for mitigation",
    )

    assign_cost = forms.BooleanField(
        label="Use Estimated Costs",
        help_text="Uncheck to treat the effort of mitigating each barrier as equal",
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
            (None, None, None, 'target_area_input'),
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

    class Meta(ScenarioForm.Meta):
        model = Project
        exclude = list(ScenarioForm.Meta.exclude)
        for f in model.output_fields():
            exclude.append(f.attname)
        widgets = {}
