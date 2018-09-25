from fishpass.models import *
from features.forms import FeatureForm
from scenarios.forms import ScenarioForm
from django import forms
from django.conf import settings
from django.forms.widgets import *
from analysistools.widgets import SliderWidget, DualSliderWidget

class ProjectForm(ScenarioForm):
    from fishpass.models import FocusArea

    focus_area = HiddenScenarioBooleanField(
        label="Filter By Boundary",
        help_text="This should be true: ALWAYS",
        initial=True
    )

    focus_area_input = forms.IntegerField(
        label="Treatment Boundary",
        help_text="This should be invisible. County, HUC, or Region Focus_Area ID",
        required=True,
    )

    def get_step_0_fields(self):
        names = [
            ('focus_area', None, None, 'focus_area_input'),
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
