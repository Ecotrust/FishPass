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

    def get_step_0_fields(self):
        names = [
            # (bool, min, max, field, [checkboxes])
            ('target_area', None, None, 'target_area_input'),
        ]
        return self._get_fields(names)

    def get_steps(self):
        return self.get_step_0_fields(),

    class Meta(ScenarioForm.Meta):
        model = Project
        exclude = list(ScenarioForm.Meta.exclude)
        for f in model.output_fields():
            exclude.append(f.attname)
        widgets = {}
