DEBUG = True

DATABASE_ENGINE = 'sqlite3'

DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.sessions',
            'object_tools',
            'object_tools.tests',
]

ROOT_URLCONF = 'object_tools.tests.urls'
