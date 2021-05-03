from django.apps import AppConfig
from django.conf import settings


class DjangoQueryCounterConfig(AppConfig):
    name = 'query_counter'
    verbose_name = 'Django Query Counter'
    _prefix = 'DQC'

    def ready(self):
        defaults = {
            'SLOWEST_COUNT': 5,
            'TABULATE_FMT': 'pretty',
            'SLOW_THRESHOLD': 1,  # seconds
            'INDENT_SQL': True,
            'PYGMENTS_STYLE': 'tango',
            'PRINT_ALL_QUERIES': True,
            'COUNT_QTY_MAP': {
                5: 'green',
                10: 'white',
                20: 'yellow',
                30: 'red',
            },
        }
        for attr, value in defaults.items():
            self._set_attr(attr, value)

    def _set_attr(self, attr, value):
        if not hasattr(settings, f'{self._prefix}_{attr}'):
            setattr(settings, f'{self._prefix}_{attr}', value)
