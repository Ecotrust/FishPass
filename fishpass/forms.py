from fishpass.models import *
from features.forms import FeatureForm, SpatialFeatureForm
from scenarios.forms import ScenarioForm
from django import forms
from django.conf import settings
from django.forms.widgets import *
from analysistools.widgets import SliderWidget, DualSliderWidget
from django.forms import ModelMultipleChoiceField, CheckboxSelectMultiple
# from scenarios.widgets import AdminFileWidget, SliderWidgetWithTooltip, DualSliderWidgetWithTooltip, CheckboxSelectMultipleWithTooltip, CheckboxSelectMultipleWithObjTooltip
from itertools import chain
from django.utils.encoding import force_text


class HiddenScenarioBooleanField(forms.BooleanField):
    # initial=False,
    widget=CheckboxInput(
        attrs={
            'class': 'parameters hidden_checkbox'
        }
    )

class BackwardCompatibleChoiceWidget(forms.widgets.ChoiceWidget):
    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        groups = []
        has_selected = False

        ######
        # It's time for some Ryan magic
        ######
        try:
            if len(value) == 1 and isinstance(eval(value[0]), (list, tuple)):
                value = eval(value[0])
        except Exception as e:
            pass
        ######
        # End Magic
        ######

        for index, (option_value, option_label) in enumerate(chain(self.choices)):
            if option_value is None:
                option_value = ''

            subgroup = []
            if isinstance(option_label, (list, tuple)):
                group_name = option_value
                subindex = 0
                choices = option_label
            else:
                group_name = None
                subindex = None
                choices = [(option_value, option_label)]
            groups.append((group_name, subgroup, index))

            for subvalue, sublabel in choices:
                selected = (
                    force_text(subvalue) in value and
                    (has_selected is False or self.allow_multiple_selected)
                )
                if selected is True and has_selected is False:
                    has_selected = True
                subgroup.append(self.create_option(
                    name, subvalue, sublabel, selected, index,
                    subindex=subindex, attrs=attrs,
                ))
                if subindex is not None:
                    subindex += 1
        return groups

class BackwardCompatibleCheckboxSelectMultiple(BackwardCompatibleChoiceWidget):
    allow_multiple_selected = True
    input_type = 'checkbox'
    template_name = 'django/forms/widgets/checkbox_select.html'
    option_template_name = 'django/forms/widgets/checkbox_option.html'

    def use_required_attribute(self, initial):
        # Don't use the 'required' attribute because browser validation would
        # require all checkboxes to be checked instead of at least one.
        return False

    def value_omitted_from_data(self, data, files, name):
        # HTML checkboxes don't appear in POST data if not checked, so it's
        # never known if the value is actually omitted.
        return False

    def id_for_label(self, id_, index=None):
        # This hook is necessary because widget has multiple HTML elements and, thus, multiple IDs.
        # https://docs.djangoproject.com/en/1.11/ref/forms/widgets/#django.forms.Widget.id_for_label
        """"
        Don't include for="field_0" in <label> because clicking such a label
        would toggle the first checkbox.
        """
        if index is None:
            return ''
        return super(BackwardCompatibleCheckboxSelectMultiple, self).id_for_label(id_, index)


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
        widget=forms.Textarea(
            attrs={
                'class': 'invisible focus-area-textarea',
            }
        ),
        label='',
        # help_text="This should be invisible. Stringified GeoJSON Multiselection of FocusAreas",
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
        # widget=forms.CheckboxSelectMultiple(),
        widget=BackwardCompatibleCheckboxSelectMultiple(),
        initial=initial_ownership,
        label="OwnershipType",
        help_text="Uncheck any ownership type that you don't wish to consider for mitigation",
    )

    assign_cost = forms.BooleanField(
        label="Use Estimated Costs",
        help_text="Uncheck to treat the effort of mitigating each barrier as equal",
        required = False,
        initial=True
    )

    budget_type = forms.ChoiceField(
        choices = (('budget', 'Fixed Budget'),('batch', 'Ranged Budget')),
        label="Budget Type",
        help_text="'Fixed Budget' for a known buget, 'Ranged Budget' to find the best ROI btween a min/max budget",
        required=True,
        initial='budget'
    )

    budget = forms.IntegerField(
        label='Budget',
        initial=0,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'currency form-control',
                'pre_text': '$',
            }
        )
    )

    budget_min = forms.IntegerField(
        required=False,
        initial=100000,
        widget=forms.NumberInput(
            attrs={
                'class': 'slidervalue currency form-control rangevalue',
                'pre_text': '$',
            }
        )
    )

    budget_max = forms.IntegerField(
        required=False,
        initial=1000000,
        widget=forms.NumberInput(
            attrs={
                'class': 'slidervalue currency form-control rangevalue',
                'pre_text': '$',
            }
        )
    )

    budget_input = forms.IntegerField(
    #     widget=DualSliderWidget(
    #         'budget_min',
    #         'budget_max',
    #         min=0,
    #         max=50000000,
    #         step=1000           #This doesn't work at all for non-assigned costs. Do we need to make 2 of these?
    #     )
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
            (None, None, None, 'budget_min'),
            (None, None, None, 'budget_max'),
            (None, None, None, 'batch_increment'),
        ]
        return self._get_fields(names)

    def get_steps(self):
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


class ProjectBarrierTypeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        from fishpass.models import BarrierType, ScenarioBarrierType
        # Get the project
        project = kwargs.pop('project')
        # Call the default init process
        super().__init__(*args, **kwargs)
        # Step through all barrier type instances
        for bartype in BarrierType.objects.all().order_by('order'):
            barrier_type_cost_field_name = "cost_type_%s" % bartype.name
            self.fields[barrier_type_cost_field_name] = forms.DecimalField(
                label=bartype.name,
                decimal_places = 2,
                required=False,
                widget=NumberInput(
                    attrs={
                        'id': 'id_%s' % barrier_type_cost_field_name,
                        'bartype': bartype.pk,
                        'project': project.pk,
                        'step': "1.0", # should this be 1000?
                        'min': "0.00",
                        'field': 'default_cost'
                    }
                )
            )
            barrier_type_postpass_field_name = "postpass_type_%s" % bartype.name
            self.fields[barrier_type_postpass_field_name] = forms.DecimalField(
                label=bartype.name,
                decimal_places = 2,
                required=False,
                widget=NumberInput(
                    attrs={
                        'id': 'id_%s' % barrier_type_postpass_field_name,
                        'step': "0.1",  # should this be 0.05?
                        'max': "1.0",
                        'min': "0.0",
                        "bartype": bartype.pk,
                        "project": project.pk,
                        "field": "default_post_passability"
                    }
                )
            )
            if project:
                proj_type, created = ScenarioBarrierType.objects.get_or_create(project=project, barrier_type=bartype)
                if created:
                    proj_type.default_cost = bartype.default_cost
                    proj_type.default_post_passability = bartype.default_post_passability
                    proj_type.save()
                self.initial[barrier_type_cost_field_name] = proj_type.default_cost
                # self.fields[barrier_type_cost_field_name].initial = proj_type.default_cost
                self.initial[barrier_type_postpass_field_name] = proj_type.default_post_passability
            else:
                self.initial[barrier_type_cost_field_name] = bartype.default_cost
                # self.fields[barrier_type_cost_field_name].initial = bartype.default_cost
                self.initial[barrier_type_postpass_field_name] = bartype.default_post_passability

    def save(self, project):
        from fishpass.models import ScenarioBarrierType, BarrierType
        for field_name in self.fields:
            field = self.fields[field_name]
            bartype = BarrierType.objects.get(pk=field.widget.attrs['bartype'])
            proj_type, created = ScenarioBarrierType.objects.get_or_create(project=project, barrier_type=bartype)
            setattr(proj_type, field.widget.attrs['field'], self.cleaned_data[field_name])
            proj_type.save()


    def as_table(self):
        return self._html_output(
            ProjectBarrierTypeForm.NormalRowFormatter(),
            u'<tr><td colspan="2">%s</td></tr>', # unused
            u'</td></tr>',
            u'<br />%s',
            False
        )

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
            # create pre-pass field for each instance
            barrier_status_prepass_field_name = "status_type_%s" % status.name
            # self.fields[barrier_status_prepass_field_name] = PrePassField(
            self.fields[barrier_status_prepass_field_name] = forms.FloatField(
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
            else:
                self.initial[barrier_status_prepass_field_name] = status.default_pre_passability

    def save(self, project):
        from fishpass.models import ScenarioBarrierStatus, BarrierStatus
        for field_name in self.fields:
            field = self.fields[field_name]
            status = BarrierStatus.objects.get(pk=field.widget.attrs['status'])
            proj_status, created = ScenarioBarrierStatus.objects.get_or_create(project=project, barrier_status=status)
            proj_status.default_pre_passability = self.cleaned_data[field_name]
            proj_status.save()

class ProjectBarrierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        from fishpass.models import Barrier, Project, ScenarioBarrier
        super().__init__(*args, **kwargs)
        self.fields['project'].widget = HiddenInput()
        self.fields['barrier'].widget = HiddenInput()

    class Meta:
        model = ScenarioBarrier
        fields = ['project', 'barrier', 'pre_pass', 'post_pass', 'cost', 'action']

class UploadPADForm(forms.Form):
    file = forms.FileField()

class UploadBarrierCostForm(forms.Form):
    file = forms.FileField()
