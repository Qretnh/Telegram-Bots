from pathlib import Path
from environs import Env

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env()

SECRET_KEY = 'django-insecure-vn7zv4o3&ouhmb^^6vx63_)oeby(=yejn&7wcr5f+6y&*qtx5='

DEBUG = True  # чтоб при каждом обновлении кода перезапускался и сервер джанги. на проде - нельзя

ALLOWED_HOSTS = []  # изменить для подключения на удалённый сервер в админку

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app'
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

ROOT_URLCONF = 'admin.urls'

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

WSGI_APPLICATION = 'admin.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DATABASE"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': 'postgres',
        'PORT': env("DB_PORT"),
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

CELERY_TASK_ALWAYS_EAGER = False  # выполнение задач асинхронно
CELERY_TASK_EAGER_PROPAGATES = True  # проброс исключений селери
CELERY_BROKER_URL = env("REDIS_URL")  # адрес хранилища для селери
CELERY_RESULT_BACKEND = env("REDIS_URL")  # тоже но другой

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# базовое логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
