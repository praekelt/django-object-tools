DEBUG = True

DATABASE_ENGINE = 'sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SECRET_KEY = '123'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'object_tools',
    'django.contrib.admin',
    'object_tools.tests'
]

ROOT_URLCONF = 'object_tools.tests.urls'
STATIC_URL = '/static/'
