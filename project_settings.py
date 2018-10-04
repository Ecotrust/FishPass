"""
Django settings for marineplanner project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""


import os
from collections import OrderedDict

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.realpath(os.path.join(BASE_DIR, '..', 'assets'))
STYLES_DIR = os.path.realpath(os.path.join(ASSETS_DIR, 'styles'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-u*-d*&7j=c7a7&k5u6e61b4-t=d8ce^2k=jhox#cn8iy8m_%d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost']


# Application definition

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'marineplanner.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'marineplanner.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'NAME': 'marineplanner',
        'USER': 'postgres',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    STYLES_DIR,
)

### Django compressor (mp-visualize/base.html)
COMPRESS_ENABLED = True
COMPRESS_URL = STATIC_URL
COMPRESS_URL_PLACEHOLDER = COMPRESS_URL
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OUTPUT_DIR = 'CACHE'
COMPRESS_STORAGE = 'compressor.storage.CompressorFileStorage'
COMPRESS_VERBOSE = False
COMPRESS_PARSER = 'compressor.parser.AutoSelectParser'
COMPRESS_DEBUG_TOGGLE = 'None'

COMPRESS_JS_COMPRESSOR = 'compressor.js.JsCompressor'
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']

COMPRESS_CSS_COMPRESSOR = 'compressor.css.CssCompressor'
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter'
]
COMPRESS_CSS_HASHING_METHOD = 'mtime'
COMPRESS_MTIME_DELAY = 10

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
    ('text/x-sass', 'django_libsass.SassCompiler'),
    ('text/less', 'lessc {infile} {outfile}'),
)
COMPRESS_CACHEABLE_PRECOMPILERS = ()

COMPRESS_CACHE_KEY_FUNCTION = 'compressor.cache.simple_cachekey'
COMPRESS_CACHE_BACKEND = 'default'

COMPRESS_OFFLINE = True
COMPRESS_OFFLINE_CONTEXT = {}
COMPRESS_OFFLINE_MANIFEST = 'manifest.json'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
]

### Note: This MUST be set before importing project_settings, even though
#       INSTALLED_APPS is the first thing project_settings sets.
#       Because... django? ¯\_(?)_/¯
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.flatpages',
    'marineplanner',
    'core',
    'compressor',
    'captcha',
    'import_export',
    # 'social.apps.django_app.default',
    # 'social_django',
    ### BEGIN INSERTED INSTALLED APPS ###
    'fishpass',
    'features',
    'manipulators',
    'accounts',
    'data_manager',
    'visualize',
    'nursery',
    'drawing',
    'rpc4django',
    'analysistools',
    'scenarios',
    ### END INSERTED INSTALLED APPS ###
    'ckeditor',
]

# GET_SCENARIOS_URL = '/get_scenarios'
# SCENARIO_FORM_URL = '/features/scenario/form/'
# SCENARIO_LINK_BASE = '/features/scenario/app_scenario'

MAP_TECH = 'ol4'
# Set below in fishpass.local_settings.py
MAPBOX_ACCESS_TOKEN=None
HERE_API_TOKEN=None
HERE_APP_CODE=None

########################################
######        LAYER DATA        ########
########################################
FOCUS_AREA_TYPES = ['HUC08', 'HUC10', 'HUC12', 'County', 'Region', 'State']
FOCUS_AREA_FIELD_ID_LOOKUP = {
    'HUC08': 'huc_08_id',
    'HUC10': 'huc_10_id',
    'HUC12': 'huc_12_id',
    'County': 'county_id',
    'Region': 'region_id',
    'State': 'state_id'
}
IMPORT_SRID = 4326

# Setting internal DB SRID to an Equal Area projection would allow us to natively calculate area.
# For now mercator is just easier.
GEOMETRY_DB_SRID = 3857

#######################
# PAD IMPORT SETTINGS #
#######################
OWNERSHIP_LOOKUP = OrderedDict({})
OWNERSHIP_LOOKUP['99'] = 'Unknown'
OWNERSHIP_LOOKUP['22'] = 'City'
OWNERSHIP_LOOKUP['16'] = 'College or university'
OWNERSHIP_LOOKUP['7'] = 'Conservation group'
OWNERSHIP_LOOKUP['23'] = 'County'
OWNERSHIP_LOOKUP['4'] = 'Federal agency'
OWNERSHIP_LOOKUP['3'] = 'Local agency'
OWNERSHIP_LOOKUP['18'] = 'Natural Resource Commission'
OWNERSHIP_LOOKUP['17'] = 'Primary or secondary school'
OWNERSHIP_LOOKUP['5'] = 'Private landowner - corporate'
OWNERSHIP_LOOKUP['6'] = 'Private landowner - noncorporate'
OWNERSHIP_LOOKUP['20'] = 'Public utility'
OWNERSHIP_LOOKUP['9'] = 'Soil and water conservation district'
OWNERSHIP_LOOKUP['10'] = 'Sporting group'
OWNERSHIP_LOOKUP['2'] = 'State agency'
OWNERSHIP_LOOKUP['12'] = 'Tribe or tribal organization'
OWNERSHIP_LOOKUP['28'] = 'Multiple/mixed'
OWNERSHIP_LOOKUP['98'] = 'NA'
OWNERSHIP_LOOKUP['8'] = 'Other'

OWNERSHIP_DEFAULT = '99'

FISH_PASSAGE_BIOS_LAYER = 'ds69'
BIOS_URL = 'https://map.dfg.ca.gov/bios/?al=ds69&col=pad_id&val='

GET_SCENARIOS_URL = '/fishpass/get_scenarios/Project/'
SCENARIO_FORM_URL = '/features/project/form/'

DS_TREATMENT_CHOICES = [
    ('adjust','Adjustable'),
    ('consider','Non-adjustable'),
    ('ignore','Excluded'),
]

try:
    ### START MODULE SETTINGS IMPORT ###
    from features.settings import *
    from scenarios.settings import *
    from accounts.settings import *
    from data_manager.settings import *
    from drawing.settings import *
    from visualize.settings import *
    ### END MODULE SETTINGS IMPORT ###
except ImportError:
    pass

# Visualize Overrides

SEARCH_DISABLED = True


# Accounts Overrides
ADMIN_URL = "/admin"
CMS_ADMIN_BUTTON = False
RECAPTCHA_PUBLIC_KEY = 'SiteKey'
RECAPTCHA_PRIVATE_KEY = 'SetInLocalSettings'


try:
    from marineplanner.local_settings import *
except ImportError:
    pass

try:
    from fishpass.local_settings import *
except ImportError:
    pass

# This seems to help with some backward compatibility
import django
django.setup()
