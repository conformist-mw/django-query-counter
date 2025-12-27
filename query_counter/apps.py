from .settings import DEFAULTS
from django.apps import AppConfig
from django.conf import settings


class DjangoQueryCounterConfig(AppConfig):
    name = 'query_counter'
    verbose_name = 'Django Query Counter'

    def ready(self):

        for attr, value in DEFAULTS.items():
            if not hasattr(settings, attr):
                setattr(settings, attr, value)
