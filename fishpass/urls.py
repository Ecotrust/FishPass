from django.conf.urls import url, include
from fishpass import views
from django.contrib.auth import views as auth_views
from django.contrib.flatpages import views as flat_views
from scenarios.views import get_scenarios
from django.views.generic import RedirectView

urlpatterns = [
    ### App URLs
    url(r'^home/?$', views.home, name="planner"),
    url(r'^app$', RedirectView.as_view(url='/app/')),
    url(r'^app/$', views.app, name="app"),
    url(r'^help/$', flat_views.flatpage, {'url': '/help/'}, name="help"),
    url(r'^about/$', flat_views.flatpage, {'url': '/about/'}, name='about'),
    url(r'demo/$', views.demo, name='demo'),
    url(r'new_project/', views.new_project, name='new_project'),
    url(r'get_scenarios/', get_scenarios, {'scenario_module_name':'fishpass', 'scenario_model_name':'Project'}),
    url(r'run_optipass/(?P<scenario_id>[\w_]+)/$', views.run_optipass),

    ### Mapping/Optimization
    url(r'^get_barrier_layer/?', views.get_barrier_layer),
    url(r'^get_focus_area_geojson_by_type/?', views.get_focus_area_geojson_by_type),
    url(r'^get_focus_area_geojson_by_ids/?', views.get_focus_area_geojson_by_ids),
    url(r'scenario_barrier/(?P<project_id>[\w_]+)/$', views.scenario_barrier),

    # project specific API
    url(r'project_barrier_status_form/(?P<project_uid>[\w_]+)/$', views.project_barrier_status_form),
    url(r'project_barrier_status_form_reset/(?P<project_uid>[\w_]+)/$', views.project_barrier_status_form_reset),
    url(r'project_barrier_type_form/(?P<project_uid>[\w_]+)/$', views.project_barrier_type_form),
    url(r'project_barrier_type_form_reset/(?P<project_uid>[\w_]+)/$', views.project_barrier_type_form_reset),
    url(r'project_barrier_form/(?P<project_uid>[\w_]+)/(?P<barrier_id>[\w_]+)/$', views.project_barrier_form),
    url(r'project_barrier_form_reset/(?P<project_uid>[\w_]+)/(?P<barrier_id>[\w_]+)/$', views.project_barrier_form_reset),

    url(r'^check_download_report/$', views.check_download_report),
    url(r'^get_user_scenario_list/$', views.get_user_scenario_list),
    # url(r'^get_report/(?P<projid>[\w_]+)/$', views.get_report),
    url(r'^get_report/(?P<projid>[\w_]+)/$', views.init_report),
    url(r'^export_report/(?P<projid>[\w_]+)/$', views.export_report),
    url(r'^get_report_geojson_by_budget/(?P<project_uid>[\w_]+)/(?P<budget>[\w_]+)/$', views.get_report_geojson_by_budget),
    url(r'^get_report_summary_by_budget/(?P<project_uid>[\w_]+)/(?P<budget>[\w_]+)/$', views.get_report_summary_by_budget),
    url(r'^get_barrier_table_headers/(?P<project_uid>[\w_]+)/$', views.get_barrier_table_headers),
    url(r'^get_barrier_report/(?P<project_uid>[\w_]+)/(?P<barrier_id>[\w_]+)/(?P<budget>[\w_]+)/$', views.get_barrier_report),
    url(r'^get_barrier_report_list/(?P<project_uid>[\w_]+)/(?P<barrier_id>[\w_]+)/(?P<budget>[\w_]+)/$', views.get_barrier_report_list),

    url(r'^$', views.home, name='home'),

    ### FlatPages
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    # url(r'^(?P<url>.*/?)$', flat_views.flatpage),
]

from django.contrib import admin
from visualize.models import Bookmark, Content
admin.site.unregister(Bookmark)
admin.site.unregister(Content)
