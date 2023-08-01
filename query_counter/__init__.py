__version__ = '0.3.1'

try:
    import django
    if django.VERSION < (3, 2):
        default_app_config = 'query_counter.apps.DjangoQueryCounterConfig'
except ImportError:
    ...
