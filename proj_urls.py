"""marineplanner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve
### INSERT ADDITIONAL IMPORTS HERE ###
import accounts.urls
from fishpass.views import get_filter_results, get_filter_count, import_PAD, import_barrier_costs
### END PROJECT URL IMPORTS ###

urlpatterns = [
    url(r'^admin/import_PAD/?', import_PAD),
    url(r'^adminfishpass/import_PAD/?', import_PAD),
    url(r'^admin/import_barrier_costs/?', import_barrier_costs),
    url(r'^adminfishpass/import_barrier_costs/?', import_barrier_costs),
    url(r'^admin/?', admin.site.urls),
    ### INSERT PROJECT URL INCLUDES HERE ###
    url(r'^features/', include('features.urls')),
    url(r'^manipulators/', include('manipulators.urls')),
    url(r'^scenarios/get_filter_results/(?P<project_id>[\w_]+)/$', get_filter_results),
    url(r'^scenarios/get_filter_results/', get_filter_results),
    url(r'^scenarios/get_filter_count', get_filter_count),
    url(r'^scenarios/', include('scenarios.urls')),
    url(r'^account/auth/', include('social.apps.django_app.urls', namespace='social')),
    url(r'^accounts/', include('accounts.urls', namespace="account")),
    url(r'^data_manager/', include('data_manager.urls')),
    url(r'^drawing/', include('drawing.urls')),
    # url(r'^visualize/', include('visualize.urls')),
    url(r'^fishpass/', include('fishpass.urls')),

    url(r'^', include('fishpass.urls')),

    # url(r'^', fishpass.views.home, name='home'),
    ### END PROJECT URL INCLUDES ###
    # url(r'^visualize/', include('visualize.urls')),
    # url(r'^account/auth/', include('social.apps.django_app.urls', namespace='social')),
    # url(r'^account/', include('accounts.urls', namespace="account")),
    # url(r'^data_manager/', include('data_manager.urls', namespace="data_manager")),
]

if settings.DEBUG:
  urlpatterns +=[
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # url(r'^static/(?P.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
  ]
