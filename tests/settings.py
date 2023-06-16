DEBUG = True
USE_TZ = False
SECRET_KEY = 'key'
INSTALLED_APPS = ['apps']
ROOT_URLCONF = 'urls'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}
