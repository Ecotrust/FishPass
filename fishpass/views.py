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

# get geo query set from focusarea model
# return geojson
def get_focus_area_geojson_by_type(request):
    from fishpass.models import FocusArea
    unit_type = settings.DEFAULT_FOCUS_AREA_TYPE
    if request.method == 'GET':
        try:
            unit_type = request.GET['unitType']
            unit_id = request.GET['unitId']
        except:
            pass
    focus_area_qs = FocusArea.objects.filter(unit_type=unit_type)
    focus_area_qs.filter(unit_id=unit_id)
    geojson = get_geojson_from_queryset(focus_area_qs)
    return JsonResponse(geojson)


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
            try:
                feat_json = {
                    "type": "Feature",
                    "geometry": json.loads(feature.geometry.geojson),
                    "properties": {}
                }
            except:
                import ipdb
                ipdb.set_trace()
        else:
            try:
                feat_json = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [feature.geometry.x, feature.geometry.y]
                    },
                    "properties": {}
                }
            except:
                import ipdb
                ipdb.set_trace()
                print('barriererror')

        # convert attributes to json notation
        if project:
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

def get_ds_ids(barrier, barrier_pad_ids, ds_ids):
    if barrier.downstream_id not in barrier_pad_ids and barrier.downstream_id not in ds_ids:
        ds_ids.append(barrier.downstream_id)
    try:
        ds_barrier = Barrier.objects.get(pad_id=downstream_id)
        ds_ids = get_ds_ids(ds_barrier, barrier_pad_ids, ds_ids)
    except:
        pass
    return ds_ids

def createOptiPassInputFile(project, file_location):
    from fishpass.models import FocusArea, Barrier, ScenarioBarrier, ScenarioBarrierType, ScenarioBarrierStatus, BarrierType, BarrierStatus
    from datetime import datetime
    # get list of barriers
    barriers = [x for x in project.run()]
    # get downstream barriers
    # if treat_downstream is 'adjust', ds_ids are already in barriers. If 'ignore' we don't want them.
    ds_barriers = []
    if project.treat_downstream == 'consider':
        ds_ids = []
        barrier_pad_ids = [x.pad_id for x in barriers]
        for barrier in barriers:
            ds_ids = get_ds_ids(barrier, barrier_pad_ids, ds_ids)
        if 0 in ds_ids:
            ds_ids.remove(0)
        for ds_id in ds_ids:
            ds_barriers.append(Barrier.objects.get(pad_id=int(ds_id)))

    barrier_dicts = []
    if len(project.target_area_input) > 1:
        fa_ids = FocusArea.objects.filter(id__in=eval(project.target_area_input))
    else:
        fa_ids = FocusArea.objects.filter(unit_type='County')

    if fa_ids.count() < 1:
        raise Exception('ERROR: fishpass.views.createOptiPassInputFile -- fa_ids MUST be at least 1!!!')

    startLoopTime = datetime.now()
    for barrier in barriers + ds_barriers:
        prepass = False
        postpass = False
        cost = False
        # NPROJ: The number of actions that can be taken on a barrier. This is not able to be greater than 1
        #   for the purposes of this tool
        nproj = 0
        # ACTION: Force project to be in the mitigation solution, 0<=consider, -1<=never, nproj<=force
        action = 0
        # FOCUS: Is the barrier in the focus area or not?
        if barrier in barriers:
            focus=1
        else:
            focus=0
        proj_barrier_records = ScenarioBarrier.objects.filter(project=project,barrier=barrier)
        # TODO: get SUPER clear on how barrierType, Status, 'fixable' and action impact focus, nproj, and action
        # You def need a decision matrix to be sure to test all cases against current tool.
        if proj_barrier_records.count() == 1:
            project_barrier = proj_barrier_records[0]
            prepass = project_barrier.pre_pass
            postpass = project_barrier.post_pass
            if project_barrier.cost:
                cost = project_barrier.cost
            if project_barrier.action == 'include':
                action = 1
            elif project_barrier.action == 'consider':
                action = 0
            elif project_barrier.action == 'exclude':
                action = -1
        if not prepass:
            proj_status_records = ScenarioBarrierStatus.objects.filter(project=project,barrier_status=barrier.barrier_status)
            if proj_status_records.count() == 1:
                proj_status = proj_status_records[0]
                prepass = proj_status.default_pre_passability
            else:
                prepass = barrier.barrier_status.default_pre_passability
        if not postpass or not cost:
            proj_type_records = ScenarioBarrierType.objects.filter(project=project,barrier_type=barrier.site_type)
            if proj_type_records.count() == 1:
                if not postpass and proj_type_records[0].default_post_passability:
                    postpass = proj_type_records[0].default_post_passability
                if not cost and proj_type_records[0].default_cost:
                    cost = proj_type_records[0].default_cost
            if not postpass:
                postpass = barrier.site_type.default_post_passability
            if not cost:
                cost = barrier.site_type.default_cost
        if not cost or not str(cost).isnumeric():
            nproj = 0
            cost = "NA"
        elif not project.assign_cost:
            cost = 1

        if not barrier.downstream_id or barrier.downstream_id == 0:
            dsid = "NA"
        else:
            dsid = barrier.downstream_id

        barrier_dict = {
            'BARID': barrier.pad_id,
            'REGION': FocusArea.objects.get(geometry__covers=barrier.geometry, unit_type=fa_ids[0].unit_type).description,    # I wonder if this should be a stringified ID
            'FOCUS': focus,
            'DSID': dsid,
            'USHAB': barrier.upstream_miles,
            'PREPASS': prepass,
            'NPROJ': nproj,
            'ACTION': action,
            'COST': cost,
            'POSTPASS': postpass,
        }

        barrier_dicts.append(barrier_dict)

    endLoopTime = datetime.now()
    if (endLoopTime-startLoopTime).total_seconds() > 10:
        print("Time to gather barrier data: %s" % str((endLoopTime - startLoopTime).total_seconds()))
    # write csv to file_location
    import csv
    fieldnames = ['BARID','REGION','FOCUS','DSID','USHAB','PREPASS','NPROJ','ACTION']
    if len(barrier_dict.keys()) == len(fieldnames) + 2:
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
                    report_obj, created = ProjectReport.objects.get_or_create(**report_dict)

def optipass(project):
    import os, subprocess, stat, shutil
    input_file = os.path.join(settings.CSV_BASE_DIR, '%s_input.csv' % project.uid)
    createOptiPassInputFile(project, input_file)
    # Sort out batch or budget soln
    budget_list = []
    if project.budget_type == 'batch':
        itr_budget = project.min_budget
        while itr_budget < project.max_budget:
            budget_list.append(itr_budget)
            itr_budget += project.batch_increment
        budget_list.append(project.max_budget)
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
        subprocess.run(process_list)

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
    action_only = False
    if request.method == 'GET':
        try:
            action_only = request.GET['action_only']
            if action_only:
                action_only = True
        except:
            pass
    if action_only:
        report = ProjectReport.objects.get(project=project, action=1)
    else:
        report = ProjectReport.objects.get(project=project)

    #TODO: generate geojson of solution
    #   Do this in a separate view
    #   Should come from scenarios.views.get_filter_results
    # TODO: sort out filter vs. all results
    #   this can be managed on front end
    context['title'] = str(project)
    context['project'] = project.to_dict()
    context['report'] = report.to_dict()
    context['barriers'] = report.barriers_dict(action_only)
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
