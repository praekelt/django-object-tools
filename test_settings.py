DEBUG = True

DATABASE_ENGINE = 'sqlite3'

INSTALLED_APPS = [
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.sessions',
            'object_tools',
            'object_tools.tests',
]
ROOT_URLCONF = 'object_tools.tests.urls'
