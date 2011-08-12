# Django settings for setwithme project.
import os
import sys

WORKDIR = os.path.dirname(__file__)

gettext = lambda s: s

# We love to put our apps in a separate directory
sys.path.append(os.path.join(WORKDIR, 'apps'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Serge Travin', 'serge.travin@gmail.com'),
    ('Anatoly Larin', 'me@alarin.ru'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en', u'En'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(WORKDIR, 'static', 'writable')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '//setwith.me/static/writable/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
COMMON_STATIC_ROOT = os.path.join(WORKDIR, 'static')
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (COMMON_STATIC_ROOT,)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'i1hi@eseca(p)m#itwrxr(dtx$4qy8b3s%696p&h&r&6wn#6*6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'core.middleware.CsrfFixMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'auth.middleware.FacebookMiddleware',
    'auth.middleware.VkontakteMiddleware',
    'users.middleware.UserOnlineMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'users.context_processors.user_profile',
)


INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = 'setwithme.urls'

TEMPLATE_DIRS = (
    os.path.join(WORKDIR, 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    # Third-party apps
    'south',
    'django_facebook',
    'celery',

    # Our apps
    'auth',
    'core',
    'users',
    'game',
    'chat',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


SITE_NAME = 'Setwithme'
SITE_DOMAIN = 'setwith.me'

AUTH_PROFILE_MODULE = 'users.UserProfile'

SESSION_SAVE_EVERY_REQUEST = True

# setwith.me
#FACEBOOK_APP_ID = '154919794582072'
#FACEBOOK_SECRET_KEY = '2f8f1719fa39fc05be74a33e28474091'

# setwithme.loc:8000
#FACEBOOK_APP_ID = '129235007167183'
#FACEBOOK_SECRET_KEY = '1f56b1a80e1d1dfb2d82c5953cf52043'

# setwithme.ep.io
FACEBOOK_APP_ID = '259283820765276'
FACEBOOK_SECRET_KEY = '4920c31ec084157c03a22f2089812039'

# setwithme.loc:8000
#VK_APP_ID = '2433440'
#VK_SECRET_KEY = 'd3NJUTrYacWLt8sXag9H'

# setwith.me
VK_APP_ID = '2434483'
VK_SECRET_KEY = '5PT6SMT3r3WWt5YQ60b5'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'auth.backends.FacebookBackend',
    'auth.backends.VkontakteBackend',
    'auth.backends.AnonymousBackend',
)

LOGIN_URL = '/'
REDIRECT_AFTER_LOGIN = '/lobby/'
REDIRECT_AFTER_LOGOUT = '/'

DEFAULT_PROFILE_PIC = os.path.join(STATIC_URL, '/static/images/nophoto.png')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

try:
    from settings_local import *
except ImportError:
    pass
