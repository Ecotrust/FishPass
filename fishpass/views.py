from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import json
from django.conf import settings
from django.views.decorators.cache import cache_page
from accounts.forms import LogInForm, SignUpForm

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
    context['title'] = 'FishPASS'
    context['MAPBOX_TOKEN'] = settings.MAPBOX_ACCESS_TOKEN
    context['HERE_TOKEN'] = settings.HERE_API_TOKEN
    context['HERE_APP_CODE'] = settings.HERE_APP_CODE
    context['MAP_TECH'] = settings.MAP_TECH
    context['SEARCH_DISABLED'] = settings.SEARCH_DISABLED
    return HttpResponse(template.render(context, request))

def home(request, template=loader.get_template('fishpass/home.html'), context={'title': 'FishPASS - Home'}):
    context['SEARCH_DISABLED'] = settings.SEARCH_DISABLED
    return HttpResponse(template.render(context, request))

def demo(request, template='fishpass/demo.html'):
    from scenarios import views as scenarios_views
    return scenarios_views.demo(request, template)

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

def get_geojson_from_queryset(query, project):
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    for feature in query:
        # derive geojson
        feat_json = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [feature.geometry.x, feature.geometry.y]
            },
            "properties": {}
        }
        # convert attributes to json notation
        feat_dict = feature.to_dict(project)
        for field in feat_dict.keys():
            feat_json['properties'][field] = feat_dict[field]

        # apply geojson to return object
        geojson['features'].append(feat_json)

    return geojson

def run_filter_query(filters):
    from collections import OrderedDict
    from fishpass.models import Barrier
    # TODO: This would be nicer if it generically knew how to filter fields
    # by name, and what kinds of filters they were. For now, hard code.
    notes = []
    query = Barrier.objects.all()

    if 'area' in filters.keys() and filters['area']:
        # RDH 1/8/18: filter(geometry__area_range(...)) does not seem available.
        # query = query.filter(geometry__area__range=(filters['area_min'], filters['area_max']))

        # RDH 1/9/18: Why can't we use the model's 'Run Filters' function?
        pu_ids = [pu.pk for pu in query if pu.geometry.area <= float(filters['area_max']) and pu.geometry.area>= float(filters['area_min'])]
        query = (query.filter(pk__in=pu_ids))

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

'''
'''
@cache_page(60 * 60) # 1 hour of caching
def get_filter_results(request, query=False, notes=[], extra_context={}):
    from features.views import check_user
    request = check_user(request)
    from django.db.models.query import QuerySet
    from django.contrib.gis.db.models.query import GeoQuerySet
    if not type(query) in [QuerySet, GeoQuerySet] :
        filter_dict = dict(request.GET.items())
        (query, notes) = run_filter_query(filter_dict)
    count = query.count()
    #TODO: get geojson. Update Barrier layer on return if ('show filter results' = True)
    geojson = None

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
        import ipbd
        ipbd.set_trace()
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

def update_scenario_barrier(request):
    #Get form values
    # get/create ScenarioBarrier record
    # Update with form values
    return JsonResponse({})


def get_report(request, projid, template=loader.get_template('fishpass/report.html'), context={'title': 'FishPASS - Report'}):
    from features.registry import get_feature_by_uid

    #TODO: Get and verify user account || sharing permissions
    # verify user ownership of project
    project = get_feature_by_uid(projid)

    #TODO: generate geojson of solution
    #   Do this in a separate view
    #   Should come from scenarios.views.get_filter_results
    # TODO: sort out filter vs. all results
    #   this can be managed on front end
    context['project'] = project.to_dict()
    return HttpResponse(template.render(context, request))

def export_report(request):
    #TODO: generate report as 1 or more CSVs and export (zipped if necessary)
    return JsonResponse({})

def run_optipass(request):
    # get scenario ID from request
    # get scenario object
    # convert scenario into optipass input format
    # run optipass command
    # consume optipass output
    # save results to scenario object
    return JsonResponse({})
