import re
import time
from collections import Counter
from operator import itemgetter
from typing import Dict, List

from django.conf import settings
from django.db import connection
from django.utils import termcolors
from tabulate import tabulate

from .settings import DEFAULTS


def _get_value(key):
    """"
    Try to get value from django.conf.settings otherwise default
    """
    return getattr(settings, key, DEFAULTS[key])


def _print(lines, sep: str = '\n') -> None:
    print(f'{sep}'.join(lines))  # noqa: T201


def colorize(string: str, color: str = 'white') -> str:
    return {
        'yellow': termcolors.make_style(opts='bold', fg='yellow'),
        'red': termcolors.make_style(opts='bold', fg='red'),
        'white': termcolors.make_style(opts='bold', fg='white'),
        'green': termcolors.make_style(opts='bold', fg='green'),
    }[color](string)


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
        self.duplicates = {}
        self.slowest = {}
        self.counted = None
        self.start = time.perf_counter()

    def __call__(self, execute, sql, params, many, context):
        stripped_sql = re.sub(r'\(%s.*\)', '(%s, ..., %s)', sql)
        current_query = {'sql': stripped_sql, 'params': params, 'many': many}
        start = time.monotonic()
        execute(sql, params, many, context)
        duration = time.monotonic() - start
        current_query['duration'] = duration
        self.queries.append(current_query)

    def do_count(self) -> Counter:
        return Counter([
            q['sql'].split()[0]
            for q in self.queries if q['sql'].startswith(self.SQL_STATEMENTS)
        ])

    def count_duplicated(self) -> Dict[str, int]:
        return {
            query: count
            for query, count
            in Counter([q['sql'] for q in self.queries]).most_common()
            if count > 1
        }

    def get_slowest(self) -> Dict[str, float]:
        return {
            q['sql']: q['duration']
            for q in sorted(
                self.queries,
                key=itemgetter('duration'),
                reverse=True,
            )[:_get_value('DQC_SLOWEST_COUNT')]
            if q['duration'] > _get_value('DQC_SLOW_THRESHOLD')
        }

    def count(self) -> None:
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
        lines_to_print = []
        print_all = _get_value('DQC_PRINT_ALL_QUERIES')
        if print_all:
            lines_to_print.extend(self.generate_all_queries_lines())
        stats = self.collect_stats()
        table = self.get_table(stats)
        if not print_all:
            lines_to_print.extend(self.generate_detailed_lines())
        lines_to_print.append(
            colorize(table, get_color_by(sum(self.duplicates.values()))),
        )

        _print(lines_to_print)

    def get_table(self, stats):
        return tabulate(
            [[value for _, value in stats]],
            headers=[h.capitalize() for h, _ in stats],
            tablefmt=_get_value('DQC_TABULATE_FMT'),
        )

    def generate_all_queries_lines(self) -> List[str]:
        lines = []
        for query, count in Counter(
            [q['sql'] for q in self.queries],
        ).most_common():
            lines.append(
                f'{colorize(str(count), color="yellow")}: {highlight(query)}',
            )
        return lines

    def generate_detailed_lines(self) -> List[str]:
        lines = []
        if self.duplicates:
            lines.append(colorize('Duplicate queries:'))
            for index, (query, count) in enumerate(self.duplicates.items()):
                if index >= _get_value('DQC_DUPLICATED_COUNT'):
                    break
                lines.append(f'{colorize(count, "yellow")}: {highlight(query)}')
        if self.slowest:
            lines.append(colorize('Slowest queries:'))
            for query, duration in self.slowest.items():
                duration = f'{duration:.2f}'
                lines.append(f'{colorize(duration, "red")}: {highlight(query)}')
        return lines


def queries_counter(func):
    def inner_func(*args, **kwargs):
        func_info = ['Target:']
        query_logger = QueryLogger()
        with connection.execute_wrapper(query_logger):
            result = func(*args, **kwargs)
        query_logger.count()
        try:
            if len(args) == 1:
                cmd, = args
                func_info.append(cmd.__module__)
            elif len(args) > 1:
                _, request, *_ = args
                if request.path:
                    func_info.append(request.path)
                if request.resolver_match:
                    func_info.append(request.resolver_match._func_path)
        except ValueError:
            func_info.append(func.__qualname__)
        query_logger.print_stats()
        _print(func_info, sep=' ')
        return result
    return inner_func
