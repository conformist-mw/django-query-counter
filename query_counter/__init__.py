import django

__version__ = '0.2.2'

if django.VERSION < (3, 2):
    default_app_config = 'query_counter.apps.DjangoQueryCounterConfig'
