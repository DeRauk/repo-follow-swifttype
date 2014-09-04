"""
Django settings for repofollow project.

"""

from os.path import join, abspath, dirname, sep

here = lambda *dirs: join(abspath(dirname(__file__)), *dirs)
BASE_DIR = here("..")

root = lambda *dirs: join(abspath(BASE_DIR), *dirs)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/


DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost']


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'rest_framework',
    'account',
    'commitfollower'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'repofollow.urls'

WSGI_APPLICATION = 'repofollow.wsgi.application'


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'\

STATIC_ROOT = root("collected_static")

STATICFILES_DIRS = (
    root("assets"),
    root("static"),
    )

TEMPLATE_DIRS = [join(BASE_DIR, 'repofollow', 'templates'),
                 join(BASE_DIR, 'account', 'templates'),
                 join(BASE_DIR, 'ordering', 'templates'),]

REST_FRAMEWORK = {
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}


LOGIN_URL="/account/login/"


# Normally all of the settings below this would be split out into a dev.py and
# prod.py file, to keep it simple I just put everything in here.


from dateutil import tz
TIME_ZONE = 'America/New_York'
TIME_ZONE_OBJ = tz.gettz(TIME_ZONE)

VCS_PROPERTIES = {
    'github.com': {
        'api_url': "https://api.github.com",
        'request_headers': {
                            'Accept': 'application/vnd.github.v3+json',
                            'Time-Zone': TIME_ZONE},
        'oauth_key': r'2ea202b5258512fd5f60',
        'oauth_token': {'access_token': 'e48db759a3d121caa8fa00f92c6786a1f52a2522'}
    }
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'repofollow',
        'USER': 'derauk',
        'PASSWORD': 'jelly',
        'HOST': 'localhost',
        'PORT': '',
        'ATOMIC_REQUESTS':True # Important: An exception during an http request
                               #            causes a rollback for all db calls
                               #            that occurred during that request
    }
}

SECRET_KEY = '(f#0$polg78*rxe)5n*z^pup(^(k+mgwb3eg29%%gpb6d4r0yr'



# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        }
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'INFO',
        },
        'repofollow': {
            'handlers':['console'],
            'propagate': True,
            'level':'DEBUG',
        },
        'account': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'commitfollower': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}
