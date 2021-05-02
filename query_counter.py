import functools
import time
from collections import Counter
from operator import itemgetter

from django.db import connection
from django.utils import termcolors
from tabulate import tabulate

__all__ = [
    'queries_counter',
    'DjangoQueryCounter'
]

DQC_SLOWEST_COUNT = 5
DQC_TABULATE_FMT = 'pretty'
DQC_SLOW_THRESHOLD = 1  # seconds
DQC_INDENT_SQL = True
DQC_PYGMENTS_STYLE = 'tango'
DQC_COUNT_QTY_MAP = {
    5: 'green',
    10: 'white',
    20: 'yellow',
    30: 'red',
}
DQC_PRINT_ALL_QUERIES = True

colorize_map = {
    'yellow': termcolors.make_style(opts='bold', fg='yellow'),
    'red': termcolors.make_style(opts='bold', fg='red'),
    'white': termcolors.make_style(opts='bold', fg='white'),
    'green': termcolors.make_style(opts='bold', fg='green'),
}


def colorize(string, color='white'):
    return colorize_map[color](string)


def get_color_by(count):
    for _count, color in DQC_COUNT_QTY_MAP.items():
        if count <= _count:
            return DQC_COUNT_QTY_MAP[_count]
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
        sql = sqlparse.format(sql, reindent=DQC_INDENT_SQL)

    if pygments:
        sql = pygments.highlight(
            sql,
            SqlLexer(),
            TerminalTrueColorFormatter(style=DQC_PYGMENTS_STYLE),
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
            )[:DQC_SLOWEST_COUNT]
            if q['duration'] > DQC_SLOW_THRESHOLD
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
        if DQC_PRINT_ALL_QUERIES:
            self.print_all_queries()
        stats = self.collect_stats()
        table = self.get_table(stats)
        print(colorize(table, get_color_by(len(self.duplicates))))
        if not DQC_PRINT_ALL_QUERIES:
            self.print_detailed()

    def get_table(self, stats):
        return tabulate(
            [[value for _, value in stats]],
            headers=[h.capitalize() for h, _ in stats],
            tablefmt=DQC_TABULATE_FMT,
        )

    def print_all_queries(self):
        for query, count in Counter(
            [q['sql'] for q in self.queries]
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


class DjangoQueryCounter:

    def __init__(self, get_response):
        self.get_response = get_response

    @queries_counter
    def __call__(self, request):
        return self.get_response(request)
