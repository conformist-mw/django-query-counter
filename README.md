# Django Queries Count

[![check](https://github.com/conformist-mw/django-query-counter/actions/workflows/check.yml/badge.svg)](https://github.com/conformist-mw/django-query-counter/actions/workflows/check.yml)
[![PyPI version](https://badge.fury.io/py/django-query-counter.svg)](https://badge.fury.io/py/django-query-counter)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-query-counter)
![PyPI - Versions from Framework Classifiers](https://img.shields.io/pypi/frameworkversions/django/django-query-counter)


The difference between this project and all the others like it is that I needed
 to debug management command in Django, but all the others only provided middleware,
 which did not solve my problem.

## Example output

![duplicates-main-example](https://user-images.githubusercontent.com/13550539/117552176-89c30b80-b052-11eb-80b9-7eb32435d116.png)

The basic idea is to count duplicate queries, like django-debug-toolbar does,
 and output them. The number of duplicated queries and the color of the theme
 can be specified in the settings. It is also possible to output all requests
 at once (counted if they are duplicated).

## Content

- [Installation](#installation)
- [Usage](#usage)
- [Available settings](#available-settings)
- [Additional screenshots](#additional-screenshots)
- [Contribute](#contribute)

## Installation

It is enough to install the package and apply the decorator to the desired
 management command or view.

```shell
pip install django-query-counter
```

Please take note that the colored and reformatted SQL output depicted in
the readme screenshots may not be achieved unless the specified additional
packages are installed (which maybe already installed):

- colorize requires [pygments](https://pypi.org/project/Pygments/)

```shell
pip install Pygments
```

- reformat requires [sqlparse](https://pypi.org/project/sqlparse/)

```shell
pip install sqlparse
```

## Usage

The project can be used in two ways:

Import the decorator and apply it where you need to know the number of queries
 to the database.

- management command:

 ```python
from django.core.management.base import BaseCommand
from query_counter.decorators import queries_counter

class Command(BaseCommand):

    @queries_counter
    def handle(self, *args, **options):
        pass
 ```

- function-based views

```python
from query_counter.decorators import queries_counter


@queries_counter
def index(request):
    pass
```

- class-based views:

```python
from django.utils.decorators import method_decorator
from query_counter.decorators import queries_counter


@method_decorator(queries_counter, name='dispatch')
class IndexView(View):
    pass
```

- specifying middleware in settings for all views at once.

```python
MIDDLEWARE = [
    'query_counter.middleware.DjangoQueryCounterMiddleware',
]
```

### Available settings

It is possible to override the default settings. To do this, you need to
 include the app to the INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...,
    'query_counter',
    ...
]
```

Default settings:

```python
{
    'DQC_SLOWEST_COUNT': 5,
    'DQC_TABULATE_FMT': 'pretty',
    'DQC_SLOW_THRESHOLD': 1,  # seconds
    'DQC_INDENT_SQL': True,
    'DQC_PYGMENTS_STYLE': 'tango',
    'DQC_PRINT_ALL_QUERIES': False,
    'DQC_COUNT_QTY_MAP': {
        5: 'green',
        10: 'white',
        20: 'yellow',
        30: 'red',
    },
}
```

Feel free to override any of them.

Tabulate tables formats you can find [here](https://github.com/astanin/python-tabulate#table-format).
Pygments styles available [here](https://pygments.org/demo/).

### Additional screenshots

![good_example](https://user-images.githubusercontent.com/13550539/117552177-8a5ba200-b052-11eb-8b6b-e66521aebdd6.png)
![yellow_example](https://user-images.githubusercontent.com/13550539/117552179-8af43880-b052-11eb-85ca-65df4eca3ea7.png)

### Contribute

Feel free to open an issue to report of any bugs. Bug fixes and features are
 welcome! Be sure to add yourself to the AUTHORS.md if you provide PR.
