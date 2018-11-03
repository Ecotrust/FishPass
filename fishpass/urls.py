from django.conf.urls import url
from fishpass import views
from django.contrib.auth import views as auth_views
from django.contrib.flatpages import views as flat_views
from scenarios.views import get_scenarios

urlpatterns = [
    ### App URLs
    url(r'^home/?$', views.home),
    url(r'^app/?$', views.app, name="app"),
    url(r'^help/$', flat_views.flatpage, {'url': '/help/'}, name="help"),
    url(r'^about/$', flat_views.flatpage, {'url': '/about/'}, name='about'),
    url(r'demo/$', views.demo, name='demo'),
    url(r'new_project/', views.new_project, name='new_project'),
    url(r'get_scenarios/', get_scenarios, {'scenario_module_name':'fishpass', 'scenario_model_name':'Project'}),
    url(r'run_optipass/(?P<scenario_id>[\w_]+)/$', views.run_optipass),

    ### Mapping/Optimization
    url(r'^get_barrier_layer/?', views.get_barrier_layer),
    url(r'^get_focus_area_geojson_by_type/?', views.get_focus_area_geojson_by_type),
    url(r'scenario_barrier/(?P<project_id>[\w_]+)/$', views.scenario_barrier),
    url(r'scenario_barrier_type/(?P<project_id>[\w_]+)/(?P<barrier_type_id>[\w_]+)/$', views.scenario_barrier_type),
    url(r'scenario_barrier_status/(?P<project_id>[\w_]+)/(?P<barrier_status_id>[\w_]+)/$', views.scenario_barrier_status),

    url(r'get_scenario_barrier_status_defaults/(?P<project_id>[\w_]+)/$', views.get_scenario_barrier_status_defaults),
    url(r'get_scenario_barrier_status/(?P<project_id>[\w_]+)/$', views.get_scenario_barrier_status),

    url(r'update_scenario_barrier/$', views.update_scenario_barrier),
    url(r'get_project_barrier_form/$', views.get_project_barrier_form),

    url(r'^get_user_scenario_list/$', views.get_user_scenario_list),
    url(r'^get_report/(?P<projid>[\w_]+)/$', views.get_report),
    url(r'^export_report/(?P<projid>[\w_]+)/$', views.export_report),

    url(r'$', views.home, name='home'),
]

from django.contrib import admin
from visualize.models import Bookmark, Content
admin.site.unregister(Bookmark)
admin.site.unregister(Content)
