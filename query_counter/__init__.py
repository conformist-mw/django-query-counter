from .query_counter import DjangoQueryCounterMiddleware  # noqa: F401
from .query_counter import queries_counter  # noqa: F401

__version__ = '0.1.0'

default_app_config = 'query_counter.apps.DjangoQueryCounterConfig'
