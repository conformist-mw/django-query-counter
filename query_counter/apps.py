from django.apps import AppConfig
from django.conf import settings

from .settings import DEFAUTLS


class DjangoQueryCounterConfig(AppConfig):
    name = 'query_counter'
    verbose_name = 'Django Query Counter'

    def ready(self):

        for attr, value in DEFAUTLS.items():
            if not hasattr(settings, attr):
                setattr(settings, attr, value)
