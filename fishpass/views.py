from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import json
from django.conf import settings
from django.views.decorators.cache import cache_page
from accounts.forms import LogInForm, SignUpForm
from django.contrib.gis.geos.collections import *

def accounts_context():
    context = {
        'form': LogInForm(),
        'login_title': 'Login',
        'login_intro': 'Access your account',
        'registration_form': SignUpForm(),
        'registration_title': ' ', # space is needed to hide the defualt and insert a &nbsp; space
        'forgot_password_link': 'Forgot Password?',
        'register_link': ' ', # space is needed to hide the defualt and insert a &nbsp; space
        'help_link': ' ', # space is needed to hide the defualt and insert a &nbsp; space
    }
    return context

# Create your views here.
def app(request, template=loader.get_template('fishpass/app.html'), context=accounts_context()):
    from fishpass.models import Project
    from datetime import datetime

    if request.user.is_authenticated:
        user_projects = Project.objects.filter(user=request.user).order_by('name')
    else:
        from django.shortcuts import redirect
        return redirect('/')

    default_project_name = "%s - %s" % (str(request.user), datetime.now().strftime("%H:%M %m/%d/%Y"))



    context['title'] = 'FishPASS'
    context['MAPBOX_TOKEN'] = settings.MAPBOX_ACCESS_TOKEN
    context['HERE_TOKEN'] = settings.HERE_API_TOKEN
    context['HERE_APP_CODE'] = settings.HERE_APP_CODE
    context['MAP_TECH'] = settings.MAP_TECH
    context['SEARCH_DISABLED'] = settings.SEARCH_DISABLED
    context['projects'] = user_projects
    context['initialProjectName'] = default_project_name
    return HttpResponse(template.render(context, request))

def new_project(request):
    from fishpass.models import Project
    if request.method == 'POST':
        project = Project.objects.create(name=request.POST['name'], user=request.user)
        return JsonResponse({'project_uid': project.uid})
    else:
        return HttpResponse('Request type must be "POST"', status=405)

def home(request, template=loader.get_template('fishpass/home.html'), context=accounts_context()):
    context['title'] = 'FishPASS - Home'
    context['SEARCH_DISABLED'] = settings.SEARCH_DISABLED
    return HttpResponse(template.render(context, request))

def demo(request, template='fishpass/demo.html'):
    from scenarios import views as scenarios_views
    return scenarios_views.demo(request, template)

# get geo query set from focusarea model
# return geojson
def get_focus_area_geojson_by_type(request):
    from fishpass.models import FocusArea
    unit_type = settings.DEFAULT_FOCUS_AREA_TYPE
    if request.method == 'GET':
        try:
            unit_type = request.GET['unitType']
        except:
            pass
        try:
            unit_id = request.GET['unitId']
        except:
            unit_id = None
            pass
    focus_area_qs = FocusArea.objects.filter(unit_type=unit_type)
    focus_area_qs = focus_area_qs.filter(unit_id=unit_id)
    geojson = get_geojson_from_queryset(focus_area_qs)
    return JsonResponse(geojson)

# get geo queryset from list of FocusArea IDs
# return geojson
def get_focus_area_geojson_by_ids(request):
    from fishpass.models import FocusArea
    if request.method == 'GET':
        try:
            fa_ids = request.GET.getlist('fa_ids[]')
        except:
            fa_ids = []
            pass
    focus_area_qs = FocusArea.objects.filter(pk__in=fa_ids)
    geojson = get_geojson_from_queryset(focus_area_qs)
    return JsonResponse(geojson)

def scenario_barrier(request, project_id, barrier_id, context={}):
    retjson = {
        'status': 200,
        'success': True,
        'message': "Successfully updated Project Barrier"
    }
    return JsonResponse(retjson)

# def scenario_barrier_type(request, project_id, context={}):
#     retjson = {
#         'status': 200,
#         'success': True,
#         'message': "Successfully updated Project Barrier Type"
#     }
#     return JsonResponse(retjson)

# def get_scenario_barrier_status_defaults(request, project_id, context={}):
#     from fishpass.models import BarrierStatus
#     if request.method == 'GET':
#         statuses = BarrierStatus.objects.all()
#         return JsonResponse(statuses.to_dict())

def get_scenario_barrier_status(request, project_id, context={}):
    # Get project from uid
    from features.registry import get_feature_by_uid
    from fishpass.models import BarrierStatus, ScenarioBarrierStatus

    project = get_feature_by_uid(project_id)
    # Query for all BarrierStatuses
    statuses = BarrierStatus.objects.all()
    # Query for any ScenarioBarrierStatuses
    scenario_barrier_statuses = ScenarioBarrierStatus.objects.filter(project=project)
    # TODO: Make status_values an ordered dict
    status_values = {}
    for status in statuses.order_by('order'):
    #   check if scenario_barrier_status override exists
        if status in scenario_barrier_statuses:
    #       status_values[BARRIER_STATUS] = scenario_barrier_status.get(status=status).pre-pass
            status_values[status.name] = scenario_barrier_statuses.get(barrier_status=status).default_pre_passability
        else:
    #       status_values[BARRIER_STATUS] = status.pre-passing
            status_values[status.name] = status.default_pre_passability
    # TODO: return json response of dict
    return JsonResponse(status_values)

# def get_scenario_barrier_type_defaults(request, project_id, context={}):
#     from fishpass.models import BarrierType
#     if request.method == 'GET':
#         types = BarrierType.objects.all()
#         return JsonResponse(types.to_dict())

def get_scenario_barrier_type(request, project_id, context={}):
    # Get project from uid
    from features.registry import get_feature_by_uid
    from fishpass.models import BarrierType, ScenarioBarrierType

    project = get_feature_by_uid(project_id)
    # Query for all BarrierStatuses
    types = BarrierType.objects.all()
    # Query for any ScenarioBarrierStatuses
    scenario_barrier_types = ScenarioBarrierType.objects.filter(project=project)
    # TODO: Make status_values an ordered dict
    type_values = {}
    for type in types.order_by('order'):
    #   check if scenario_barrier_status override exists
        if type in scenario_barrier_types:
    #       type_values[BARRIER_TYPE] = scenario_barrier_types.get(barrier_type=TYPE)
            type_values['%s' % (type,)] = scenario_barrier_types.get(barrier_type='%s' % (type,))
        else:
    #       type_values[BARRIER_TYPE] = status.pre-passing
            type_values['%s' % (type,)] = '%s' % (type,)
    # TODO: return json response of dict
    return JsonResponse(type_values)
#
# def update_scenario_barrier(request):
#     # if form.is_valid():
#         # Get form values
#         # get/create ScenarioBarrier record
#         # Update with form values
#     return JsonResponse({})
#
# def scenario_barrier_status(request, project_id, context={}):
#     # if request.method == 'POST':
#         # get_or_create
#     retjson = {
#         'status': 200,
#         'success': True,
#         'message': "Successfully updated Project Barrier Status"
#     }
#     return JsonResponse(retjson)

def project_barrier_status_form_reset(request, project_uid, context={}):
    if request.user.is_authenticated():
        from fishpass.models import Project, ScenarioBarrierStatus
        project_id = int(project_uid.split('_')[-1])
        project = Project.objects.get(pk=project_id)
        for status in ScenarioBarrierStatus.objects.filter(project=project):
            status.delete()
        request.method = 'GET'
    return project_barrier_status_form(request, project_uid, context=context)

def project_barrier_status_form(request, project_uid, template=loader.get_template('fishpass/modals/project_barrier_modal_form.html'), context={}):
    if request.user.is_authenticated():
        from fishpass.forms import ProjectBarrierStatusForm
        from fishpass.models import Project
        project_id = int(project_uid.split('_')[-1])
        project = Project.objects.get(pk=project_id)
        if request.method == 'POST':
            form = ProjectBarrierStatusForm(request.POST,project=project)
            if form.is_valid():
                try:
                    form.save(project)
                    retjson = {
                        'status': 200,
                        'success': True,
                        'message': "Successfully updated Project Barrier Status"
                    }
                except Exception as e:
                    retjson = {
                        'status': 500,
                        'success': False,
                        'message': e.message
                    }
            else:
                retjson = {
                    'status': 406,  # 406: Not Acceptable
                    'success': False,
                    'message': "Form is not valid"
                }
            return JsonResponse(retjson)
        else:
            project_barrier_status_form = ProjectBarrierStatusForm(project=project)
            context['project_barrier_form'] = project_barrier_status_form
            context['project_barrier_form_id'] = 'project-barrier-status-form'
            return HttpResponse(template.render(context, request))
    return None

def project_barrier_type_form_reset(request, project_uid, context={}):
    if request.user.is_authenticated():
        from fishpass.models import Project, ScenarioBarrierType
        project_id = int(project_uid.split('_')[-1])
        project = Project.objects.get(pk=project_id)
        for status in ScenarioBarrierType.objects.filter(project=project):
            status.delete()
        request.method = 'GET'
    return project_barrier_type_form(request, project_uid, context=context)

def project_barrier_type_form(request, project_uid, template=loader.get_template('fishpass/modals/project_barrier_modal_form_type.html'), context={}):
    if request.user.is_authenticated():
        from fishpass.forms import ProjectBarrierTypeForm
        from fishpass.models import Project
        project_id = int(project_uid.split('_')[-1])
        project = Project.objects.get(pk=project_id)
        if request.method == 'POST':
            form = ProjectBarrierTypeForm(request.POST,project=project)
            if form.is_valid():
                try:
                    form.save(project)
                    retjson = {
                        'status': 200,
                        'success': True,
                        'message': "Successfully updated Project Barrier Type"
                    }
                except Exception as e:
                    retjson = {
                        'status': 500,
                        'success': False,
                        'message': e.message
                    }
            else:
                retjson = {
                    'status': 406,  # 406: Not Acceptable
                    'success': False,
                    'message': "Form is not valid"
                }
            return JsonResponse(retjson)
        else:
            project_barrier_type_form = ProjectBarrierTypeForm(project=project)
            context['project_barrier_form'] = project_barrier_type_form
            context['project_barrier_form_id'] = 'project-barrier-type-form'
            return HttpResponse(template.render(context, request))
    return None

def project_barrier_form(request, project_uid, barrier_id, template=loader.get_template('fishpass/modals/project_barrier_modal_form.html'), context={}):
    from fishpass.models import ScenarioBarrier
    if request.user.is_authenticated():
        from fishpass.forms import ProjectBarrierForm
        from fishpass.models import Project, Barrier
        project_id = int(project_uid.split('_')[-1])
        project = Project.objects.get(pk=project_id)
        barrier = Barrier.objects.get(pad_id=barrier_id)
        (project_barrier, created) = ScenarioBarrier.objects.get_or_create(project=project,barrier=barrier)
        if request.method == 'POST':
            form = ProjectBarrierForm(request.POST,instance=project_barrier)
            if form.is_valid():
                try:
                    form.save()
                    retjson = {
                        'status': 200,
                        'success': True,
                        'message': "Successfully updated Project Barrier"
                    }
                except Exception as e:
                    retjson = {
                        'status': 500,
                        'success': False,
                        'message': e.message,
                        'form': None
                    }
            else:
                retjson = {
                    'status': 406,  # 406: Not Acceptable
                    'success': False,
                    'message': "Form is not valid",
                    'form': form.as_table()
                }
            return JsonResponse(retjson)
        else:
            initial = {}
            if not project_barrier.pre_pass and project_barrier.barrier.barrier_status:
                initial['pre_pass'] = project_barrier.barrier.barrier_status.default_pre_passability
            if not project_barrier.post_pass and project_barrier.barrier.site_type:
                initial['post_pass'] = project_barrier.barrier.site_type.default_post_passability
            if not project_barrier.cost and project_barrier.barrier.site_type:
                initial['cost'] = project_barrier.barrier.site_type.default_cost
            project_barrier_form = ProjectBarrierForm(instance=project_barrier, initial=initial)
            context['project_barrier_form'] = project_barrier_form
            context['project_barrier_form_id'] = 'project-barrier-form'
            return HttpResponse(template.render(context, request))
    return None

def project_barrier_form_reset(request, project_uid, barrier_id, context={}):
    if request.user.is_authenticated():
        from fishpass.models import Project, ScenarioBarrier, Barrier
        project_id = int(project_uid.split('_')[-1])
        project = Project.objects.get(pk=project_id)
        barrier = Barrier.objects.get(pad_id=barrier_id)
        ScenarioBarrier.objects.filter(project=project, barrier=barrier).delete()
        request.method = 'GET'
    return project_barrier_form(request, project_uid, barrier_id, context=context)

def generate_report_csv(project_uid, report_type):
    import os
    from fishpass.models import ProjectReport, ProjectReportBarrier, Barrier
    from features.registry import get_feature_by_uid
    import csv

    try:
        project = get_feature_by_uid(project_uid)
    except Exception as e:
        print('ERROR: Could not get project from project UID: %s' % project_uid)
        return None

    report_list = ProjectReport.objects.filter(project=project).order_by('budget')
    if report_list.count() < 1:
        print('ERROR: No Project Report found for project: %s' % project_uid)
        return None

    if report_type == 'all':
        csv_file_suffix = '_export_all.csv'
        barrier_list = [x.barrier_id for x in ProjectReportBarrier.objects.filter(project_report=report_list[0])]
    else:
        csv_file_suffix = '_export_filtered.csv'
        barrier_list = []
        for report in report_list:
            barrier_list += [x.barrier_id for x in ProjectReportBarrier.objects.filter(project_report=report, action=1)]
            barrier_list = list(set(barrier_list))

    barrier_list.sort()

    csv_filename = os.path.join(settings.MEDIA_ROOT,'reports','%s%s' % (project_uid, csv_file_suffix))

    # TODO: if assigned costs, cost_unit = '$', else cost_unit = 'count'
    cost_unit = '$'

    if report_list.count() > 1:
        top_index = report_list.count()-1
        project_report_items = [
            ('Min Budget (%s):' % cost_unit, report_list[0].budget),
            ('Max Budget (%s):' % cost_unit, report_list[top_index].budget),
            ('Budget Step Size (%s):' % cost_unit, project.batch_increment)
        ]
    else:
        project_report_items = [
            ('Budget (%s):' % cost_unit, report_list[0].budget),
        ]

    barrier_items_header_dicts = [
        {'label': 'PAD-ID', 'field': 'pad_id', 'project_specific': False},
        {'label': 'Estimated Cost ($)', 'field': 'estimated_cost', 'project_specific': True},
        {'label': 'Barriers Downstream', 'field': 'downstream_barrier_count', 'project_specific': False},
        {'label': 'Site Type', 'field': 'site_type', 'project_specific': False},
        {'label': 'Site Name', 'field': 'site_name', 'project_specific': False},
    ]
    barrier_items_header_list = [x['label'] for x in barrier_items_header_dicts]

    for report in report_list:
        barrier_items_header_list.append('Action')
        # barrier_items_header_list.append('Ptnl. Hab')

    barrier_dict = {}
    barrier_reports = ProjectReportBarrier.objects.filter(barrier_id__in=barrier_list, project_report__in=report_list).order_by('project_report__budget')
    # For each barrier
    for index, barrier_id in enumerate(barrier_list):
        barrier_id_reports = barrier_reports.filter(barrier_id=barrier_id).order_by('project_report__budget')
        # if index == 0:
        barrier_report = barrier_id_reports[0]
        barrier = Barrier.objects.get(pad_id=int(barrier_id))
        barrier_dict[str(barrier_id)] = {}
        for field in barrier_items_header_dicts:
            if field['project_specific']:
                value = getattr(barrier_report, field['field'])
            else:
                value = getattr(barrier, field['field'])
            barrier_dict[str(barrier_id)][field['label']] = str(value)
        barrier_dict[str(barrier_id)]['Actions'] = []
        # For each budget report instance for that barrier
        for barrier_report in barrier_id_reports:
            if barrier_report.action == 0:
                barrier_action = 'DO NOT FIX'
            else:
                barrier_action = 'REMEDIATE'
            barrier_dict[str(barrier_id)]['Actions'].append(barrier_action)

    barrier_items_list = []
    for barrier_id in barrier_list:
        action_count = 0
        barrier_item_row = []
        for key in barrier_items_header_list:
            if not key == 'Action':
                try:
                    barrier_item_row.append(str(barrier_dict[str(barrier_id)][key]))
                except TypeError as e:
                    import ipdb; ipdb.set_trace()
                    print(e)
            else:
                barrier_item_row.append(barrier_dict[str(barrier_id)]['Actions'][action_count])
                action_count += 1
        barrier_items_list.append(barrier_item_row)

    action_index = barrier_items_header_list.index('Action')

    action_field_names = [
        {'label': 'Budget (%s)' % cost_unit, 'field': 'budget'},
        {'label': 'Estimated Cost (%s)' % cost_unit, 'field': 'cost'},
        {'label': 'Ptnl. Habitat (mi)', 'field': 'ptnl_habitat'},
        {'label': 'Ptnl. Habitat Gain (mi)', 'field': 'netgain'},
    ]
    action_field_rows = []
    for action_field_name in action_field_names:
        action_field_row = [''] * (action_index-1)
        action_field_row.append(action_field_name['label'])
        for budget in report_list:
            if action_field_name['field'] == 'cost':
                action_field_row.append(budget.cost())
            else:
                action_field_row.append(getattr(budget,action_field_name['field']))
        action_field_rows.append(action_field_row)

    required_row_length = len(barrier_items_header_list)
    blank_row = [''] * required_row_length

    with open(csv_filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for project_report_item in project_report_items:
            new_row = [project_report_item[0], project_report_item[1]] + [''] * (required_row_length - 2)
            writer.writerow(new_row)

        writer.writerow(blank_row)
        for action_field_row in action_field_rows:
            while len(action_field_row) < required_row_length:
                action_field_row += ['']
            writer.writerow(action_field_row)

        writer.writerow(barrier_items_header_list)
        for barrier_item in barrier_items_list:
            while len(barrier_item) < required_row_length:
                barrier_item += ['']
            writer.writerow(barrier_item)

def check_download_report(request):
    import os
    from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
    from django.core.cache import cache
    from fishpass import celery
    if request.method == "GET":
        data = request.GET
    else:
        # We don't care if this is GET or POST - the result should be the same
        data = request.POST
    try:
        project_uid = data['project_uid']
        report_type = data['report_type']
        timer = data['timer']
    except Exception as e:
        return HttpResponseBadRequest('request requires project_uid, report_type, and timer arguments')

    if report_type == 'all':
        csv_file_suffix = '_export_all.csv'
    else:
        csv_file_suffix = '_export_filtered.csv'

    csv_filename = os.path.join(settings.MEDIA_ROOT,'reports','%s%s' % (project_uid, csv_file_suffix))

    if os.path.isfile(csv_filename):
        json = {
            'available': True,
            'link': '/media/reports/%s%s' % (project_uid, csv_file_suffix)
        }
        return JsonResponse(json)
    else:
        if int(timer) >= 60:
            cache_key = "%s_%s_report_task_id" % (project_uid, report_type)
            celery_task = cache.get(cache_key)

            if not celery_task or celery.app.AsyncResult(celery_task).status == 'PENDING' :
                # Do this as a separate process!
                celery_task = celery.run_view.delay('fishpass', 'generate_report_csv', project_uid, report_type)
                cache.set(cache_key, celery_task.task_id, 60*60*24*7)
                # generate_report_csv(project_uid, report_type)
        return JsonResponse({
            'available': False,
            'link': None
        })


def get_user_scenario_list(request):
    #TODO: use "scenarios.views.get_scenarios" if possible.
    from fishpass.models import Project
    user_scenarios_list = []
    user_scenarios = Project.objects.filter(user=request.user)
    for us in user_scenarios:
        user_scenarios_list.append({
            "id": us.pk,
            "name": us.name,
            "description": us.description,
        })
    return JsonResponse(sorted(user_scenarios_list, key=lambda k: k['name'].lower()), safe=False)

def get_report_geojson_from_reports(barrier_reports):
    from fishpass.models import Barrier
    from django.core.cache import cache
    cache_key = "%s_report_geojson" % '_'.join([str(x.pk) for x in barrier_reports.order_by('pk')])
    geojson = cache.get(cache_key)

    if not geojson:
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        for barrier_report in barrier_reports:
            feature = Barrier.objects.get(pad_id=int(barrier_report.barrier_id))
            # derive geojson
            if hasattr(feature, 'geometry') and (type(feature.geometry) == Polygon or type(feature.geometry) == MultiPolygon):
                feat_json = {
                    "type": "Feature",
                    "geometry": json.loads(feature.geometry.geojson),
                    "properties": {}
                }
            else:
                feat_json = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [feature.geometry.x, feature.geometry.y]
                    },
                    "properties": {}
                }
            feat_json['properties']['id'] = feature.pk
            feat_json['properties']['pad_id'] = feature.pad_id
            feat_json['properties']['action'] = barrier_report.action
            feat_json['properties']['site_name'] = feature.site_name
            feat_json['properties']['stream_name'] = feature.stream_name
            feat_json['properties']['status'] = feature.barrier_status.name
            feat_json['properties']['status_color'] = feature.barrier_status.color
            geojson['features'].append(feat_json)


    return geojson


def get_geojson_from_queryset(query, project=None, cache_key=None):
    from django.core.cache import cache
    if cache_key:
        geojson = cache.get(cache_key)
    else:
        geojson = None
    if not geojson:
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        for feature in query:
            # derive geojson
            if hasattr(feature, 'geometry') and (type(feature.geometry) == Polygon or type(feature.geometry) == MultiPolygon):
                feat_json = {
                    "type": "Feature",
                    "geometry": json.loads(feature.geometry.geojson),
                    "properties": {}
                }
            else:
                feat_json = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [feature.geometry.x, feature.geometry.y]
                    },
                    "properties": {}
                }

            # convert attributes to json notation
            if hasattr(feature, 'to_dict'):
                feat_dict = feature.to_dict(project)
                for field in feat_dict.keys():
                    feat_json['properties'][field] = feat_dict[field]
            else:
                feat_json['properties']['id'] = feature.pk
            # apply geojson to return object
            geojson['features'].append(feat_json)

        if cache_key:
            cache.set(cache_key, geojson, 60*60*24*7)

    return geojson

def run_filter_query(filters):
    from collections import OrderedDict
    from fishpass.models import Barrier, OwnershipType, FocusArea
    # TODO: This would be nicer if it generically knew how to filter fields
    # by name, and what kinds of filters they were. For now, hard code.
    notes = []
    query = Barrier.objects.all()

    if 'ownership_input' in filters.keys() and filters['ownership_input'] == 'true':
        if 'ownership_input_checkboxes' in filters.keys() and filters['ownership_input_checkboxes'] == 'true':
            ownership_keys = []
            for ot_id in [x.pk for x in OwnershipType.objects.all()]:
                ot_label = 'ownership_input_checkboxes_%d' % ot_id
                if ot_label in filters.keys() and filters[ot_label] == 'true':
                    ownership_keys.append(ot_id)
            query = query.filter(ownership_type__in=ownership_keys)

    if 'target_area_input' in filters.keys() and len(filters['target_area_input']) > 0:
        focus_ids = []
        for fa_id_raw in filters['target_area_input'].split(','):
            fa_id = int(fa_id_raw.strip())
            target = FocusArea.objects.get(pk=fa_id)
            focus_ids = focus_ids + [x.pad_id for x in query.filter(geometry__intersects=target.geometry)]
        # remove dupes
        focus_ids = list(set(focus_ids))
        query = query.filter(pad_id__in=focus_ids)

    if 'treat_downstream' in filters.keys() and filters['treat_downstream'] == 'true':
        if 'treat_downstream_input' in filters.keys() and filters['treat_downstream_input'] == 'adjust':
            focus_ids = [x.pad_id for x in query]
            ds_ids = []
            for barrier in query:
                ds_ids = get_ds_ids(barrier, focus_ids, ds_ids)
            query_ids = focus_ids + ds_ids
            query = Barrier.objects.filter(pad_id__in=query_ids)

    return (query, notes)

'''
'''
@cache_page(60 * 60) # 1 hour of caching
def get_filter_count(request, query=False, notes=[]):
    from django.db.models.query import QuerySet
    from django.contrib.gis.db.models.query import GeoQuerySet
    if not type(query) in [QuerySet, GeoQuerySet] :
        filter_dict = dict(request.GET.items())
        (query, notes) = run_filter_query(filter_dict)
    return HttpResponse(query.count(), status=200)

def get_project_min_max(query, project):
    from numbers import Number
    from collections.abc import Iterable
    min = None
    max = None
    available_project_count = 0
    enforced_min = None
    for barrier in query:
        bar_dict = barrier.to_dict(project)
        if bar_dict['fixable'] and bar_dict['action'] != 'exclude' and bar_dict['pre_passability'] < bar_dict['post_passability']:
            available_project_count += 1
            if isinstance(bar_dict['estimated_cost'], Number):
                estimated_cost = bar_dict['estimated_cost']
            elif isinstance(bar_dict['estimated_cost'], Iterable) and len(bar_dict['estimated_cost']) == 2 and (type(bar_dict['estimated_cost'][1]) == float or type(bar_dict['estimated_cost'][1]) == int):
                estimated_cost = bar_dict['estimated_cost'][1]
            else:
                estimated_cost = False
            if estimated_cost:
                if max:
                    max += estimated_cost
                else:
                    max = estimated_cost
                if min:
                    if min > estimated_cost:
                        min = estimated_cost
                else:
                    min = estimated_cost
                if bar_dict['action'] == 'include':
                    if enforced_min:
                        if enforced_min > estimated_cost:
                            enforced_min = estimated_cost
                    else:
                        enforced_min = estimated_cost

    if enforced_min:
        print("Enforced Min = %s" % enforced_min )
        min = enforced_min
    return (min, max, available_project_count)

'''
'''
@cache_page(60 * 60) # 1 hour of caching
def get_filter_results(request, project_id=None, query=False, notes=[], extra_context={}):
    from fishpass.models import ScenarioBarrier
    from features.views import check_user
    request = check_user(request)
    from django.db.models.query import QuerySet
    from django.contrib.gis.db.models.query import GeoQuerySet
    from features.registry import get_feature_by_uid
    if not type(query) in [QuerySet, GeoQuerySet] :
        filter_dict = dict(request.GET.items())
        (query, notes) = run_filter_query(filter_dict)
    count = query.count()

    user_override_cache_key = False
    target_area_cache_key = False
    treat_downstream_cache_key = False
    ownership_cache_key = False

    if project_id:
        project = get_feature_by_uid(project_id)
        (min_cost, max_cost, available_project_count) = get_project_min_max(query, project)
        try:
            user_override_cache_key = "%s_overrides" % '_'.join([str(x.pk) for x in ScenarioBarrier.objects.filter(project=project).order_by('pk')])
        except TypeError as e:
            pass
    else:
        project = None
        min_cost = None
        max_cost = None
        available_project_count = None

    if 'target_area' in filter_dict.keys() and 'target_area_input' in filter_dict.keys() and filter_dict['target_area'] == 'true' and not filter_dict['target_area_input'] in ['', None]:
        try:
            target_area_keys = filter_dict['target_area_input'].split(',')
            target_area_keys.sort()
            target_area_cache_key = '_'.join(target_area_keys)
        except Exception as e:
            pass

    if 'treat_downstream' in filter_dict.keys() and 'treat_downstream_input' in filter_dict.keys():
        treat_downstream_cache_key = "%s_treat_downstream" % str(filter_dict['treat_downstream_input'])

    if 'ownership_input' in filter_dict.keys() and filter_dict['ownership_input'] == 'true' and 'ownership_input_checkboxes' in filter_dict.keys() and filter_dict['ownership_input_checkboxes'] == 'true':
        ownership_boxes = []
        for key in filter_dict.keys():
            if 'ownership_input_checkboxes_' in key and filter_dict[key] == 'true':
                ownership_boxes.append(key.split('ownership_input_checkboxes_')[1])
        if len(ownership_boxes) > 0:
            ownership_boxes.sort()
            ownership_cache_key = "%s_ownership" % '_'.join(ownership_boxes)

    cache_key_parts = []
    if user_override_cache_key:
        cache_key_parts.append(user_override_cache_key)
    if target_area_cache_key:
        cache_key_parts.append(target_area_cache_key)
    if treat_downstream_cache_key:
        cache_key_parts.append(treat_downstream_cache_key)
    if ownership_cache_key:
        cache_key_parts.append(ownership_cache_key)

    if len(cache_key_parts) > 0:
        cache_key = '%s_barrier_geojson' % '_'.join(cache_key_parts)
    else:
        cache_key = 'blank_barrier_geojson'

    if 'assign_cost_input' in request.GET.keys() and request.GET['assign_cost_input'] == 'false':
        min_cost = 1
        max_cost = available_project_count

    # get geojson. Update Barrier layer on return if ('show filter results' = True)
    geojson = get_geojson_from_queryset(query, project, cache_key)

    results_dict = {
        'count': count,
        'geojson': geojson,
        'min_cost': min_cost,
        'max_cost': max_cost,
        'notes': notes
    }
    try:
        # For Py 3.5 and better:
        return_dict = {**results_dict, **extra_context}
    except:
        return_dict = results_dict
        for key in extra_context.keys():
            return_dict[key] = extra_context[key]
    return_json = [return_dict]

    # return # of grid cells and dissolved geometry in geojson
    return HttpResponse(json.dumps(return_json))

# @cache_page(60 * 60) # 1 hour of caching
def get_barrier_layer(request, project=None, query=False, notes=[],extra_context={}):
    from features.views import check_user
    # Query for barriers and convert to geojson here.
    # TODO: Include any ScenarioBarrierType, ScenarioBarrierStatus, ScenarioBarrier data
    request = check_user(request)
    from django.db.models.query import QuerySet
    from django.contrib.gis.db.models.query import GeoQuerySet
    if not type(query) in [QuerySet, GeoQuerySet] :
        filter_dict = dict(request.GET.items())
        (query, notes) = run_filter_query(filter_dict)
    json = []
    count = query.count()

    try:
        geojson = get_geojson_from_queryset(query, project)
    except:
        geojson = []


    results_dict = {
        'count': count,
        'geojson': geojson,
        'notes': notes
    }
    try:
        # For Py 3.5 and better:
        return_dict = {**results_dict, **extra_context}
    except:
        return_dict = results_dict
        for key in extra_context.keys():
            return_dict[key] = extra_context[key]

    return_json = [return_dict]
    return JsonResponse(return_dict)

def get_ds_ids(barrier, focus_ids, ds_ids):
    from fishpass.models import Barrier
    if barrier.downstream_id != 0 and barrier.downstream_barrier_count > 0:
        if barrier.downstream_id not in focus_ids and barrier.downstream_id not in ds_ids:
            ds_ids.append(barrier.downstream_id)
        ds_barrier = Barrier.objects.get(pad_id=barrier.downstream_id)
        ds_ids = get_ds_ids(ds_barrier, focus_ids, ds_ids)
    return ds_ids

def create_init_barrier_dict(barrier, focus_barriers, fa_type, barrier_type, barrier_status):
    from fishpass.models import FocusArea
    if barrier in focus_barriers:
        focus = 1
    else:
        focus = 0
    if not barrier.downstream_id or barrier.downstream_id == 0:
        dsid = "NA"
    else:
        dsid = barrier.downstream_id
    # TODO: The problem the code below works around should NEVER happen!
    try:
        region = FocusArea.objects.get(geometry__covers=barrier.geometry, unit_type=fa_type).description
    except:
        regions = FocusArea.objects.filter(geometry__covers=barrier.geometry, unit_type=fa_type)
        if regions.count() > 0:
            region = regions[0].description
        else:
            region = None

    barrier_dict = {
        'BARID': barrier.pad_id,
        'REGION': region,
        'FOCUS': focus,
        'DSID': dsid,
        'USHAB': barrier.upstream_miles,
        'PREPASS': barrier_status.default_pre_passability,
        'POSTPASS': barrier_type.default_post_passability,
        'COST': barrier_type.default_cost,
        'NPROJ': 0,
        'ACTION': 0,
    }
    if not barrier_dict['COST'] == None:
        barrier_dict['NPROJ'] = 1
    return barrier_dict

def apply_project_specific_type_defaults(barrier_dict, barrier_type):
    if not barrier_type.default_cost == None:
        barrier_dict['COST'] = barrier_type.default_cost
    if not barrier_type.default_post_passability == None:
        barrier_dict['POSTPASS'] = barrier_type.default_post_passability
    return barrier_dict

def apply_project_specific_status_defaults(barrier_dict, barrier_status):
    if not barrier_status.default_pre_passability == None:
        barrier_dict['PREPASS'] = barrier_status.default_pre_passability
    return barrier_dict

def apply_project_specific_barrier_details(barrier_dict, barrier_record):
    if not barrier_record.pre_pass == None:
        barrier_dict['PREPASS'] = barrier_record.pre_pass
    if not barrier_record.post_pass == None:
        barrier_dict['POSTPASS'] = barrier_record.post_pass
    if not barrier_record.cost == None:
        barrier_dict['COST'] = barrier_record.cost
    if barrier_record.action == 'exclude':
        barrier_dict['ACTION'] = -1
    elif barrier_record.action == 'include':
        barrier_dict['ACTION'] = 1
    else:               # barrier_record.action == 'consider'
        barrier_dict['ACTION'] = 0
    return barrier_dict

def createOptiPassInputFile(project, file_location):
    # import required libraries
    from fishpass.models import FocusArea, Barrier, BarrierCost, ScenarioBarrier, ScenarioBarrierType, ScenarioBarrierStatus, BarrierType, BarrierStatus
    from fishpass.models import ProjectReport, ProjectReportBarrier
    from datetime import datetime
    # start timer
    startFuncTime = datetime.now()
    print('Beginning createOptiPassInputFile...')
    # get list of barriers
    barriers = [x for x in project.run()]
    barCrunchTime = (datetime.now()-startFuncTime).total_seconds()
    print("Filtering Done: %s seconds" % str(barCrunchTime))

    # get downstream barriers (9% runtime)
    # if treat_downstream is 'adjust', ds_ids are already in barriers. If 'ignore' we don't want them.
    ds_barriers = []
    ds_ids = []
    barrier_pad_ids = [x.pad_id for x in barriers]
    for barrier in barriers:
        # TODO: Store pre-made downstream ID list for each barrier, either in DB or cache
        ds_ids = get_ds_ids(barrier, barrier_pad_ids, ds_ids)
    if 0 in ds_ids:
        ds_ids.remove(0)
    for ds_id in ds_ids:
        ds_barriers.append(Barrier.objects.get(pad_id=int(ds_id)))
    dsBarTime = (datetime.now()-startFuncTime).total_seconds()-barCrunchTime
    print("DownStream ID Discovery Done: %s seconds" % str(dsBarTime))

    # get initial queries (0% runtime)
    barrier_dicts = []
    if len(project.target_area) > 1:
        target_ids = eval(project.target_area)
        if hasattr(target_ids, '__iter__'):
            fa_ids = FocusArea.objects.filter(id__in=target_ids)
        else:
            fa_ids = FocusArea.objects.filter(id__in=[target_ids])
    else:
        fa_ids = FocusArea.objects.filter(unit_type='County')

    if fa_ids.count() < 1:
        raise Exception('ERROR: fishpass.views.createOptiPassInputFile -- fa_ids MUST be at least 1!!!')

    fa_type = fa_ids[0].unit_type

    all_barriers = barriers + ds_barriers

    project_barrier_types = ScenarioBarrierType.objects.filter(project=project)
    project_barrier_statuses = ScenarioBarrierStatus.objects.filter(project=project)
    barrier_overrides = BarrierCost.objects.filter(pad_id__in=[x.pad_id for x in all_barriers])
    project_barriers_records = ScenarioBarrier.objects.filter(project=project)
    startLoopTime = datetime.now()
    print('Initial queries complete: %s seconds' % str((startLoopTime-startFuncTime).total_seconds()-barCrunchTime-dsBarTime))

    # gather barrier data (90% of runtime!)
    # TODO: Speed this up
    # Pre-populate ProjectReport and ProjectReportBarrier records
    projectReports = ProjectReport.objects.filter(project=project)
    longest_loop_time = 0.0
    for barrier in all_barriers:
        midLoopTime = datetime.now()

        barrier_type = barrier.site_type
        barrier_status = barrier.barrier_status
        barrier_override = False

        if barrier_overrides.count() > 0:
            try:
                barrier_override = barrier_overrides.get(pad_id=barrier.pad_id)
                if not barrier_override.site_type == None:
                    barrier_type = barrier_override.site_type
                if not barrier_override.barrier_status == None:
                    barrier_status = barrier_override.barrier_status
            except:
                barrier_override = False
                pass

        barrier_dict = create_init_barrier_dict(barrier, barriers, fa_type, barrier_type, barrier_status)
        if project_barrier_types.count() > 0:
            try:
                project_barrier_type = project_barrier_types.get(barrier_type=barrier_type)
                barrier_dict = apply_project_specific_type_defaults(barrier_dict, project_barrier_type)
            except:
                pass
        if project_barrier_statuses.count() > 0:
            try:
                project_barrier_status = project_barrier_statuses.get(barrier_type=barrier_status)
                barrier_dict = apply_project_specific_status_defaults(barrier_dict, project_barrier_status)
            except:
                pass
        if barrier_override and not barrier_override.cost == None:
            barrier_dict['COST'] = barrier_override.cost
        if project_barriers_records.count() > 0:
            try:
                project_barrier_record = project_barriers_records.get(barrier=barrier)
                barrier_dict = apply_project_specific_barrier_details(barrier_dict, project_barrier_record)
            except:
                pass

        if not type(barrier_dict['COST']) == float and not str(barrier_dict['COST']).isnumeric():
            barrier_dict['NPROJ'] = 0
            barrier_dict['COST'] = 0
            barrier_dict['POSTPASS'] = barrier_dict['PREPASS']
        else:
            barrier_dict['NPROJ'] = 1
            if not project.assign_cost:
                barrier_dict['COST'] = 1
        if barrier_dict['POSTPASS'] == None:
            barrier_dict['POSTPASS'] = barrier_dict['PREPASS']

        if not barrier.downstream_id or barrier.downstream_id == 0:
            barrier_dict['DSID'] = "NA"

        barrier_dicts.append(barrier_dict)

        if project.treat_downstream == 'adjust' or barrier in barriers:
            for projectReport in projectReports:
                projectReportBarrier = ProjectReportBarrier.objects.create(project_report=projectReport, barrier_id=barrier.pad_id, estimated_cost=barrier_dict['COST'], pre_passability=barrier_dict['PREPASS'], post_passability=barrier_dict['POSTPASS'])

        loopTime = (midLoopTime-datetime.now()).total_seconds()
        if loopTime > longest_loop_time:
            longest_loop_time = loopTime

    endLoopTime = datetime.now()
    totalTime = (endLoopTime-startFuncTime).total_seconds()
    if totalTime > 10:
        print("Time to gather barrier data: %s" % str(totalTime))
        avgLoopTime = (endLoopTime-startLoopTime).total_seconds()/len(all_barriers)
        print("%d loops averaging %s sec per loop, the longest taking %s" % (len(all_barriers), str(avgLoopTime), str(longest_loop_time)))
    # write csv to file_location
    import csv
    fieldnames = ['BARID','REGION','FOCUS','DSID','USHAB','PREPASS','NPROJ','ACTION']
    if len(barrier_dicts) > 0 :
        if len(barrier_dicts[0].keys()) == len(fieldnames) + 2:
            fieldnames = fieldnames + ['COST','POSTPASS']
        else:
            num_runs = (len(barrier_dict.keys()) - len(fieldnames))/2
            for count in [x for x in range(1,num_rows+1)]:
                fieldnames.append('COST%d' % count)
                fieldnames.append('POSTPASS%d' % count)
    with open(file_location, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for bar_dict in barrier_dicts:
            writer.writerow(bar_dict)
    return file_location

def addOutfileToReport(outfile, project):
    # working off the assumption that we aren't passing wieghts, or multiple
    #   projects or targets, this header should stay consistent

    from fishpass.models import ProjectReport, ProjectReportBarrier
    report_dict = {'project': project}
    report_objs = ProjectReport.objects.filter(project=project)
    reading_project_summary = True
    report_dicts = []
    # report_obj = False

    with open(outfile) as txt:
        # TODO: make this work for batch runs
        for row in txt:
            if not reading_project_summary:
                if not row == '\n' and 'BARID' not in row and 'ACTION' not in row and '\t' in row:
                    for index, value in enumerate(row.split('\t')):
                        value = value.replace('\n','')
                        # barrier_record = row.split('\t')
                        if index == 0:
                            barrier_id = value
                        else:
                            if int(value) in [0,1]:
                                #this record should have been created and mostly populated during 'createOptipassInputFile'
                                projReportBarrier, created = ProjectReportBarrier.objects.get_or_create(project_report=report_dicts[index-1], barrier_id=barrier_id)
                                projReportBarrier.action = int(value)
                                projReportBarrier.save()
                                # ProjectReportBarrier.objects.create(project_report=report_obj, barrier_id=barrier_record[0], action=int(barrier_record[1]))
            else:
                attribute = row.split('\t')[0].replace(':','')
                if attribute not in ['BUDGET', 'STATUS', '%OPTGAP','PTNL_HABITAT','NETGAIN']:
                    # Save projectReports
                    for report_dict in report_dicts:
                        report_dict.save()
                        reading_project_summary = False
                for index, value in enumerate(row.split('\t')):
                    value = value.replace('\n','')
                    if index > 0:
                        if attribute == 'BUDGET':
                            report_dicts.append(report_objs.get(budget=int(float(value))))
                        else:
                            if attribute == 'STATUS':
                                format_val = value
                            else:
                                format_val = float(value)
                            setattr(report_dicts[index-1],attribute.lower().replace('%',''),format_val)

def run_optipass(request, scenario_id):
    from features.registry import get_feature_by_uid
    project = get_feature_by_uid(scenario_id)
    try:
        optipass(project)
        return HttpResponse(request)
    except Exception as e:
        # TODO: collect and report Error back to initiation page
        print(str(e))
        return HttpResponse(status=500)

def optipass(project):
    import os, subprocess, stat, shutil
    from fishpass.models import ProjectReport, ProjectReportBarrier

    # clear out old report records
    ProjectReportBarrier.objects.filter(project_report__project=project).delete()
    ProjectReport.objects.filter(project=project).delete()

    # Sort out batch or budget soln
    budget_list = []
    if project.budget_type == 'batch':
        itr_budget = project.budget_min
        while itr_budget < project.budget_max:
            budget_list.append(itr_budget)
            itr_budget += project.batch_increment
        budget_list.append(project.budget_max)
    else:
        budget_list.append(project.budget)

    for budget in budget_list:
        ProjectReport.objects.create(project=project, budget=budget)

    # create input file
    input_file = os.path.join(settings.CSV_BASE_DIR, '%s_input.csv' % project.uid)
    createOptiPassInputFile(project, input_file)

    # Downstream treatment strategy
    if project.treat_downstream == 'adjust':
        dsbar_impacts = 0
    elif project.treat_downstream == 'ignore':
        dsbar_impacts = 2
    else:
        dsbar_impacts = 1

    # Craft command
    for count, budget in enumerate(budget_list):
        outfile = os.path.join(settings.CSV_BASE_DIR, "%s_output_%d.txt" % (project.uid, count))
        subprocess.run([ 'touch', outfile ])
        os.chmod(outfile, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        process_list = [
            settings.OPTIPASS_PROGRAM,
            "-f", input_file,
            "-o", outfile,
            "-b", str(budget),
            "-d", str(dsbar_impacts),
            ">", "/dev/null", "2>&1"    #Let's not overload our logs with the output
        ]

        # Run Command
        run_result = subprocess.run(process_list)
        if run_result.returncode != 0:
            raise ValueError

        # Convert output into project report
        addOutfileToReport(outfile, project)

        # remove output file
        os.remove(outfile)

    # Delete input file
    os.remove(input_file)
    return project

def get_report(request, projid, template=loader.get_template('fishpass/report.html'), passed_context={'title': 'FishPASS - Report'}):
    import os.path
    from features.registry import get_feature_by_uid
    from fishpass.models import ProjectReport, ProjectReportBarrier, BarrierStatus
    from django.core.cache import cache
    from datetime import datetime

    # start timer
    startFuncTime = datetime.now()

    #TODO: Get and verify user account || sharing permissions
    # verify user ownership of project
    project = get_feature_by_uid(projid)
    #TODO: support filters on action vs. non-action
    action_only = False
    if request.method == 'GET':
        try:
            action_only = request.GET['action_only']
            if action_only:
                action_only = True
        except:
            pass

    if action_only:
        cache_key = "get_report_%s_action_only" % projid
    else:
        cache_key = "get_report_%s" % projid

    context = cache.get(cache_key)

    if not context:
        context=passed_context
        if action_only:
            reports = ProjectReport.objects.filter(project=project, action=1)
        else:
            reports = ProjectReport.objects.filter(project=project)

        # TODO: sort out filter vs. all results
        #   this can be managed on front end
        print("GETTING REPORTS_DICT...")
        reports_dict = {}
        for report in reports.order_by('budget'):
            reports_dict[str(report.budget)] = report.to_dict()
        reportsDictTime = (datetime.now()-startFuncTime).total_seconds()
        print("GET REPORTS_DICT TIME: %d seconds" % reportsDictTime)

        print("GETTING REPORTS_LIST...")
        reports_list = []
        for report in reports.order_by('budget'):
            all_barriers = report.barriers_list(action_only)
            action_barriers = all_barriers.filter(action=1).order_by('barrier_id')
            untouched_barriers = all_barriers.filter(action=0).order_by('barrier_id')
            reports_list.append(
                {
                    'report': report.to_dict(),
                    'barriers': [x.barrier_id for x in all_barriers],
                    'action_barriers': [x.barrier_id for x in action_barriers],
                    'untouched_barriers': [x.barrier_id for x in untouched_barriers]
                }
            )
        # reports_list = [{'report': x.to_dict(), 'barriers':x.barriers_dict(action_only)} for x in reports.order_by('budget')]
        reportsListTime = (datetime.now()-startFuncTime).total_seconds()-reportsDictTime
        print("GET REPORTS_DICT TIME: %d seconds" % reportsListTime)

        report_all_csv_filename = os.path.join(settings.MEDIA_ROOT,'reports','%s_export_all.csv' % projid)
        report_filtered_csv_filename = os.path.join(settings.MEDIA_ROOT,'reports','%s_export_filtered.csv' % projid)
        if os.path.isfile(report_all_csv_filename):
            context['DOWNLOAD_ALL'] = True
        else:
            context['DOWNLOAD_ALL'] = False
        if os.path.isfile(report_filtered_csv_filename):
            context['DOWNLOAD_FILTERED'] = True
        else:
            context['DOWNLOAD_FILTERED'] = False

        context['title'] = str(project)
        context['MAPBOX_TOKEN'] = settings.MAPBOX_ACCESS_TOKEN
        context['HERE_TOKEN'] = settings.HERE_API_TOKEN
        context['HERE_APP_CODE'] = settings.HERE_APP_CODE
        context['MAP_TECH'] = settings.MAP_TECH
        context['SEARCH_DISABLED'] = settings.SEARCH_DISABLED
        context['project'] = project.to_dict()
        context['reports'] = reports_list
        context['INIT_BUDGET'] = reports_list[0]['report']['budget_int']
        context['ALL_BARRIER_LIST'] = reports_list[0]['barriers']
        context['GEOJSON'] = json.dumps({})

        # Cache for 1 week, will be reset if layer data changes
        cache.set(cache_key, context, 60*60*24*7)

    context['LEGEND'] = [[x.name, x.color] for x in BarrierStatus.objects.all().order_by('order')]

    # context['barriers'] = report.barriers_dict(action_only)
    return HttpResponse(template.render(context, request))

def export_report(request, projid):
    #TODO: generate report as 1 or more CSVs and export (zipped if necessary)
    return JsonResponse({})

'''
given a data_manager fixture file name, load the data into the database
fixture must be a string of the file location.
'''
def load_PAD_file(infile, user):
    import os, json
    from django.core import management
    from django.db.models.fields.files import FieldFile
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django.core.files.storage import default_storage

    if not user.has_perm('fishpass.add_barrier'):
        return {
            'success': False,
            'errors': ['User not permitted to add barriers.'],
            'warnings': [],
            'import_count': None
        }

    if type(infile) == InMemoryUploadedFile:
        from django.core.files.storage import default_storage
        infile_name = infile.name

        with default_storage.open(infile_name, 'wb+') as destination:
            for chunk in infile.chunks():
                destination.write(chunk)


    elif type(infile) == FieldFile:
        infile_name = infile.file.name

    else:
        infile_name = str(infile)

    infile_name = os.path.join(settings.MEDIA_ROOT, infile_name)

    try:
        json_dict_response = management.call_command('import_PAD', infile_name)
        response = json.loads(json_dict_response)
    except:
        return {
            'success': False,
            'errors': ['PAD IMPORT FAILED - Internal error'],
            'warnings': [],
            'import_count': None
        }
    try:
        os.remove(infile_name)
    except:
        pass
    else:
        return response

def load_barrier_cost_file(infile, user):
    import os, json
    from django.core import management
    from django.db.models.fields.files import FieldFile
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django.core.files.storage import default_storage

    if not user.has_perm('fishpass.add_barriercost'):
        return {
            'success': False,
            'errors': ['User not permitted to add barrier-specific data.'],
            'warnings': [],
            'import_count': None
        }

    if type(infile) == InMemoryUploadedFile:
        from django.core.files.storage import default_storage
        infile_name = infile.name

        with default_storage.open(infile_name, 'wb+') as destination:
            for chunk in infile.chunks():
                destination.write(chunk)


    elif type(infile) == FieldFile:
        infile_name = infile.file.name

    else:
        infile_name = str(infile)

    infile_name = os.path.join(settings.MEDIA_ROOT, infile_name)

    try:
        json_dict_response = management.call_command('import_barrier_costs', infile_name)
        response = json.loads(json_dict_response)
    except:
        return {
            'success': False,
            'errors': ['BARRIER DATA IMPORT FAILED - Internal error'],
            'warnings': [],
            'import_count': None
        }
    try:
        os.remove(infile_name)
    except:
        pass
    else:
        return response

def import_PAD(request, template=loader.get_template('admin/import_PAD.html'), extra_context={}):
    from django.core import management
    from fishpass.forms import UploadPADForm
    extra_context['errors'] = []
    extra_context['warnings'] = []
    extra_context['success'] = None
    if request.method == 'POST':
        form = UploadPADForm(request.POST, request.FILES)
        if form.is_valid():
            response = load_PAD_file(request.FILES['file'], request.user)
            if response['success'] and len(response['errors']) == 0:
                if len(response['warnings']) > 0:
                    extra_context['warnings'] = response['warnings']
                extra_context['success'] = 'Success: %d barriers imported!' % response['import_count']
            else:
                if len(response['errors']) > 0:
                    extra_context['errors'] = response['errors']
                if len(response['warnings']) > 0:
                    extra_context['warnings'] = response['warnings']
    else:
        form = UploadPADForm()
    context =  {
        'form': form
    }

    context.update(extra_context)
    return HttpResponse(template.render(context, request))

def import_barrier_costs(request, template=loader.get_template('admin/import_barrier_cost.html'), extra_context={}):
    from django.core import management
    from fishpass.forms import UploadBarrierCostForm
    extra_context['errors'] = []
    extra_context['warnings'] = []
    extra_context['success'] = None
    if request.method == 'POST':
        form = UploadBarrierCostForm(request.POST, request.FILES)
        if form.is_valid():
            response = load_barrier_cost_file(request.FILES['file'], request.user)
            if response['success'] and len(response['errors']) == 0:
                if len(response['warnings']) > 0:
                    extra_context['warnings'] = response['warnings']
                extra_context['success'] = 'Success: %d barrier-specific records imported!' % response['import_count']
            else:
                if len(response['errors']) > 0:
                    extra_context['errors'] = response['errors']
                if len(response['warnings']) > 0:
                    extra_context['warnings'] = response['warnings']
    else:
        form = UploadBarrierCostForm()
    context =  {
        'form': form
    }

    context.update(extra_context)
    return HttpResponse(template.render(context, request))

def get_report_geojson_by_budget(request, project_uid, budget):
    from fishpass.models import ProjectReport, ProjectReportBarrier
    from features.registry import get_feature_by_uid
    project = get_feature_by_uid(project_uid)
    report = ProjectReport.objects.get(project=project, budget=budget)
    barrier_reports = ProjectReportBarrier.objects.filter(project_report=report)
    # barrier_query = Barrier.objects.filter(pad_id__in=report.barriers_list())
    # generate geojson of solution
    # geojson = get_geojson_from_queryset(barrier_query, project)
    geojson = get_report_geojson_from_reports(barrier_reports)
    return JsonResponse(geojson)

def get_barrier_report(request, project_uid, barrier_id, budget):
    from fishpass.models import ProjectReport, ProjectReportBarrier
    from features.registry import get_feature_by_uid
    project = get_feature_by_uid(project_uid)
    project_report = ProjectReport.objects.get(project=project, budget=budget)
    barrier = ProjectReportBarrier.objects.get(project_report=project_report, barrier_id=barrier_id)
    context = {
        'barrier_dict': barrier.to_dict()
    }
    template=loader.get_template('fishpass/report_barrier.html')
    return HttpResponse(template.render(context, request))
