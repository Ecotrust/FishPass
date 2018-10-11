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
    url(r'get_scenarios/', get_scenarios, {'scenario_module_name':'fishpass', 'scenario_model_name':'Project'}),

    ### Mapping/Optimization
    url(r'^get_barrier_layer/$', views.get_barrier_layer),
    url(r'^get_focus_area_geojson_by_type/?', views.get_focus_area_geojson_by_type),

    url(r'^get_user_scenario_list/$', views.get_user_scenario_list),
    url(r'^get_report/(?P<projid>[\w_]+)/$', views.get_report),
    url(r'^export_report/(?P<projid>[\w_]+)/$', views.export_report),

    url(r'$', views.home, name='home'),
]

from django.contrib import admin
from visualize.models import Bookmark, Content
admin.site.unregister(Bookmark)
admin.site.unregister(Content)
