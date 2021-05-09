import functools
import time
from collections import Counter
from operator import itemgetter

from django.conf import settings
from django.db import connection
from django.utils import termcolors
from tabulate import tabulate

from .settings import DEFAUTLS

colorize_map = {
    'yellow': termcolors.make_style(opts='bold', fg='yellow'),
    'red': termcolors.make_style(opts='bold', fg='red'),
    'white': termcolors.make_style(opts='bold', fg='white'),
    'green': termcolors.make_style(opts='bold', fg='green'),
}


def _get_value(key):
    """"
    Try to get value from django.conf.settings otherwise default
    """
    return getattr(settings, key, DEFAUTLS[key])


def colorize(string, color='white'):
    return colorize_map[color](string)


def get_color_by(count):
    for _count, color in _get_value('DQC_COUNT_QTY_MAP').items():
        if count <= _count:
            return _get_value('DQC_COUNT_QTY_MAP')[_count]
    return color


def highlight(sql):
    try:
        import pygments
        from pygments.formatters import TerminalTrueColorFormatter
        from pygments.lexers import SqlLexer
    except ImportError:
        pygments = None

    try:
        import sqlparse
    except ImportError:
        sqlparse = None

    # strip repeated `%s, %s, ..., %s` with ellipsis
    sql = sql.strip().replace('%s, ', '').replace('%s', '%s, ..., %s')

    if sqlparse:
        sql = sqlparse.format(sql, reindent=_get_value('DQC_INDENT_SQL'))

    if pygments:
        sql = pygments.highlight(
            sql,
            SqlLexer(),
            TerminalTrueColorFormatter(style=_get_value('DQC_PYGMENTS_STYLE')),
        )
    return sql


class QueryLogger:

    SQL_STATEMENTS = ('SELECT', 'INSERT', 'UPDATE', 'DELETE')

    def __init__(self):
        self.queries = []
        self.duplicates = []
        self.slowest = []
        self.counted = []
        self.start = time.perf_counter()

    def __call__(self, execute, sql, params, many, context):
        current_query = {'sql': sql, 'params': params, 'many': many}
        start = time.monotonic()
        execute(sql, params, many, context)
        duration = time.monotonic() - start
        current_query['duration'] = duration
        self.queries.append(current_query)

    def do_count(self):
        return Counter([
            q['sql'].split()[0]
            for q in self.queries if q['sql'].startswith(self.SQL_STATEMENTS)
        ])

    def count_duplicated(self):
        return {
            query: count
            for query, count
            in Counter([q['sql'] for q in self.queries]).most_common()
            if count > 1
        }

    def get_slowest(self):
        return {
            q['sql']: q['duration']
            for q in sorted(
                self.queries,
                key=itemgetter('duration'),
                reverse=True,
            )[:_get_value('DQC_SLOWEST_COUNT')]
            if q['duration'] > _get_value('DQC_SLOW_THRESHOLD')
        }

    def count(self):
        self.elapsed = time.perf_counter() - self.start
        self.counted = self.do_count()
        self.slowest = self.get_slowest()
        self.duplicates = self.count_duplicated()

    def collect_stats(self):
        stats = [(stmt, self.counted[stmt]) for stmt in self.SQL_STATEMENTS]
        stats.extend(
            [
                ('duplicates', sum(self.duplicates.values())),
                ('total', len(self.queries)),
                ('duration', '{:.2f}'.format(self.elapsed)),
            ],
        )
        return stats

    def print_stats(self):
        print_all = _get_value('DQC_PRINT_ALL_QUERIES')
        if print_all:
            self.print_all_queries()
        stats = self.collect_stats()
        table = self.get_table(stats)
        print(colorize(table, get_color_by(sum(self.duplicates.values()))))
        if not print_all:
            self.print_detailed()

    def get_table(self, stats):
        return tabulate(
            [[value for _, value in stats]],
            headers=[h.capitalize() for h, _ in stats],
            tablefmt=_get_value('DQC_TABULATE_FMT'),
        )

    def print_all_queries(self):
        for query, count in Counter(
            [q['sql'] for q in self.queries],
        ).most_common():
            print(f'{colorize(count, color="yellow")}: {highlight(query)}')

    def print_detailed(self):
        if self.duplicates:
            print(colorize('Duplicate queries:'))
            for query, count in self.duplicates.items():
                print(f'{colorize(count, "yellow")}: {highlight(query)}')
        if self.slowest:
            print(colorize('Slowest queries:'))
            for query, duration in self.slowest.items():
                duration = f'{duration:.2f}'
                print(f'{colorize(duration, "red")}: {highlight(query)}')


def queries_counter(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        query_logger = QueryLogger()
        with connection.execute_wrapper(query_logger):
            result = func(*args, **kwargs)
        query_logger.count()
        try:
            print('Target func:', func.__qualname__)
        except AttributeError:
            pass
        query_logger.print_stats()

        return result
    return inner_func