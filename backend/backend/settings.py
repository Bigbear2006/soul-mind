from pathlib import Path

from celery.schedules import crontab
from environs import Env

env = Env()
env.read_env()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth'
        '.password_validation.UserAttributeSimilarityValidator',
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {
        'NAME': 'django.contrib.auth'
        '.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth'
        '.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = 'static'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Auth user model
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-user-model

AUTH_USER_MODEL = 'core.User'


# Logging configuration
# https://docs.djangoproject.com/en/5.2/ref/settings/#logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'django_file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': BASE_DIR / 'logs/django.log',
        },
        'bot_file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': BASE_DIR / 'logs/bot.log',
        },
    },
    'loggers': {
        'bot': {
            'handlers': ['bot_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['django_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# Celery configuration options
# https://docs.celeryq.dev/en/latest/django/first-steps-with-django.html

CELERY_BROKER_URL = env('CELERY_BROKER_URL')

CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = False

CELERY_BEAT_SCHEDULE = {
    'send_daily_quests': {
        'task': 'core.tasks.send_daily_quests',
        'schedule': crontab(minute='0', hour='8'),
    },
    'send_weekly_quests_tasks': {
        'task': 'core.tasks.send_weekly_quests_tasks',
        'schedule': crontab(minute='0', hour='8'),
    },
    'send_quests_reminders': {
        'task': 'core.tasks.send_quests_reminders',
        'schedule': crontab(minute='0', hour='16'),
    },
    'send_new_weekly_quest_is_available': {
        'task': 'core.tasks.send_new_weekly_quest_is_available',
        'schedule': crontab(minute='0', hour='10', day_of_month='1'),
    },
    'send_universe_advice_messages': {
        'task': 'core.tasks.send_universe_advice_messages',
        'schedule': crontab(minute='0', hour='10,14', day_of_week='1-5'),
    },
    'send_universe_advice_weekend_messages': {
        'task': 'core.tasks.send_universe_advice_messages',
        'schedule': crontab(minute='0', hour='11,15', day_of_week='6,0'),
    },
    'send_university_advice_extended_messages': {
        'task': 'core.tasks.send_university_advice_extended_messages',
        'schedule': crontab(minute='0', hour='10,14', day_of_week='1-5'),
    },
    'send_university_advice_extended_weekend_messages': {
        'task': 'core.tasks.send_university_advice_extended_messages',
        'schedule': crontab(minute='0', hour='11,15', day_of_week='6,0'),
    },
    'send_destiny_guide_messages': {
        'task': 'core.tasks.send_destiny_guide_messages',
        'schedule': crontab(minute='0', hour='19', day_of_week='0'),
    },
    'send_friday_gift_messages': {
        'task': 'core.tasks.send_friday_gift_messages',
        'schedule': crontab(minute='0', hour='19', day_of_week='5'),
    },
    'send_power_day_messages': {
        'task': 'core.tasks.send_power_day_messages',
        'schedule': crontab(minute='0', hour='10'),
    },
}
