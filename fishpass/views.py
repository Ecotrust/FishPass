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

    # TODO: instead of redirecting user to accounts login, add login form to project creation model
    if request.user.is_authenticated:
        user_projects = Project.objects.filter(user=request.user).order_by('name')
    else:
        return render(request, 'accounts/login.html')

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
                    import ipdb; ipdb.set_trace()
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

def get_geojson_from_queryset(query, project=None):
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
    from features.views import check_user
    request = check_user(request)
    from django.db.models.query import QuerySet
    from django.contrib.gis.db.models.query import GeoQuerySet
    from features.registry import get_feature_by_uid
    if not type(query) in [QuerySet, GeoQuerySet] :
        filter_dict = dict(request.GET.items())
        (query, notes) = run_filter_query(filter_dict)
    count = query.count()

    if project_id:
        project = get_feature_by_uid(project_id)
        (min_cost, max_cost, available_project_count) = get_project_min_max(query, project)
    else:
        project = None
        min_cost = None
        max_cost = None
        available_project_count = None

    if 'assign_cost_input' in request.GET.keys() and request.GET['assign_cost_input'] == 'false':
        min_cost = 1
        max_cost = available_project_count

    # get geojson. Update Barrier layer on return if ('show filter results' = True)
    # we don't want the 'project' data since it may not match our current (unsaved) form
    geojson = get_geojson_from_queryset(query, None)

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
    from fishpass.models import FocusArea, Barrier, BarrierCost, ScenarioBarrier, ScenarioBarrierType, ScenarioBarrierStatus, BarrierType, BarrierStatus
    from datetime import datetime
    startFuncTime = datetime.now()
    print('Beginning createOptiPassInputFile...')
    # get list of barriers
    barriers = [x for x in project.run()]
    barCrunchTime = (datetime.now()-startFuncTime).total_seconds()
    print("Filtering Done: %s seconds" % str(barCrunchTime))

    # get downstream barriers
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
    report_obj = False

    with open(outfile) as txt:
        for row in txt:
            if report_obj:
                if not row == '\n' and 'BARID' not in row and 'ACTION' not in row and '\t' in row:
                    barrier_record = row.split('\t')
                    if int(barrier_record[1]) in [0,1]:
                        ProjectReportBarrier.objects.create(project_report=report_obj, barrier_id=barrier_record[0], action=int(barrier_record[1]))
            else:
                if 'BUDGET:' in row:
                    report_dict['budget'] = float(row.split('\t')[1])
                elif 'STATUS:' in row:
                    report_dict['status'] = row.split('\t')[1].split('\n')[0]
                elif '%OPTGAP:' in row:
                    report_dict['optgap'] = float(row.split('\t')[1])
                elif 'PTNL_HABITAT:' in row:
                    report_dict['ptnl_habitat'] = float(row.split('\t')[1])
                elif 'NETGAIN:' in row:
                    report_dict['netgain'] = float(row.split('\t')[1])
                elif row == '\n':
                    ProjectReport.objects.filter(project=project).delete()
                    report_obj, created = ProjectReport.objects.get_or_create(**report_dict)

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
    input_file = os.path.join(settings.CSV_BASE_DIR, '%s_input.csv' % project.uid)
    createOptiPassInputFile(project, input_file)
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

def get_report(request, projid, template=loader.get_template('fishpass/report.html'), context={'title': 'FishPASS - Report'}):
    from features.registry import get_feature_by_uid
    from fishpass.models import ProjectReport, ProjectReportBarrier

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
        reports = ProjectReport.objects.filter(project=project, action=1)
    else:
        reports = ProjectReport.objects.filter(project=project)


    # TODO: sort out filter vs. all results
    #   this can be managed on front end
    reports_dict = {}
    for report in reports.order_by('budget'):
        reports_dict[str(report.budget)] = report.to_dict()
    reports_list = [{'report': x.to_dict, 'barriers':x.barriers_dict(action_only)} for x in reports.order_by('budget')]

    context['title'] = str(project)
    context['MAPBOX_TOKEN'] = settings.MAPBOX_ACCESS_TOKEN
    context['HERE_TOKEN'] = settings.HERE_API_TOKEN
    context['HERE_APP_CODE'] = settings.HERE_APP_CODE
    context['MAP_TECH'] = settings.MAP_TECH
    context['SEARCH_DISABLED'] = settings.SEARCH_DISABLED
    context['project'] = project.to_dict()
    context['reports'] = reports_list
    if reports.count() > 0:
        from fishpass.models import Barrier
        barrier_ids = [int(x) for x in reports[0].barriers_dict().keys()]
        barrier_query = Barrier.objects.filter(pad_id__in=barrier_ids)
        # generate geojson of solution
        geojson = get_geojson_from_queryset(barrier_query, project)
        context['GEOJSON'] = json.dumps(geojson)
    else:
        context['GEOJSON'] = json.dumps({})

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
