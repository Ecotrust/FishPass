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
    user_scenarios_list = []
    #TODO: Replace "TreatmentScenario" with BarrierScenario
    user_scenarios = TreatmentScenario.objects.filter(user=request.user)
    for us in user_scenarios:
        user_scenarios_list.append({
            "id": us.pk,
            "name": us.name,
            "description": us.description,
        })
    return JsonResponse(sorted(user_scenarios_list, key=lambda k: k['name'].lower()), safe=False)

def get_barrier_layer(request):
    # Query for barriers and convert to geojson here.
    return JsonResponse({})

def get_report(request, template=loader.get_template('fishpass/home.html'), context={'title': 'FishPASS - Report'}):
    return HttpResponse(template.render(context, request))

def export_report(request):
    #TODO: generate report as 1 or more CSVs and export (zipped if necessary)
    return JsonResponse({})
