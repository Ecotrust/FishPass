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
    return HttpResponse(template.render(context, request))

def home(request, template=loader.get_template('fishpass/home.html'), context={'title': 'FishPASS - Home'}):
    return HttpResponse(template.render(context, request))

def get_user_scenario_list(request):
    #TODO: use "scenarios.views.get_scenarios" if possible.
    user_scenarios_list = []
    user_scenarios = Project.objects.filter(user=request.user)
    for us in user_scenarios:
        user_scenarios_list.append({
            "id": us.pk,
            "name": us.name,
            "description": us.description,
        })
    return JsonResponse(sorted(user_scenarios_list, key=lambda k: k['name'].lower()), safe=False)

def get_geojson_from_queryset(query):
    geojson = {}
    # for object in query
    #     derive geojson
    #     apply geojson to return object
    #     convert attributes to json notation
    #     apply attributes to geojson feature collection
    return geojson

# @cache_page(60 * 60) # 1 hour of caching
def get_barrier_layer(request, query=False, notes=[],extra_context={}):
    # Query for barriers and convert to geojson here.
    #TODO: Look to re-use as much of scenarios.views.get_filter_results as possible
    #TODO: Include any ScenarioBarrierType, ScenarioBarrierStatus, ScenarioBarrier data
    request = check_user(request)
    from django.db.models.query import QuerySet
    from django.contrib.gis.db.models.query import GeoQuerySet
    if not type(query) in [QuerySet, GeoQuerySet] :
        filter_dict = dict(request.GET.items())
        (query, notes) = run_filter_query(filter_dict)
    json = []
    count = query.count()

    geojson = get_geojson_from_queryset(query)

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
    return JsonResponse(return_json)

def update_scenario_barrier(request):
    #Get form values
    # get/create ScenarioBarrier record
    # Update with form values
    return JsonResponse({})


def get_report(request, projectId, template=loader.get_template('fishpass/home.html'), context={'title': 'FishPASS - Report'}):
    # NOTE: YES THIS IS IT'S OWN TEMPLATE/PAGE!!!
    # Get and verify user account
    # verify user ownership of project
    # Generate project tabular content
    #   Do this in a separate view
    # generate barrier-specific tabular content
    #   Do this in a separate view
    # generate geojson of solution
    #   Do this in a separate view
    # TODO: sort out filter vs. all results
    #   this can be managed on front end
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
