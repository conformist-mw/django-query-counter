from setuptools import setup

from query_counter import __version__

url = (
    'https://github.com/conformist-mw/django-query-counter/'
    'tarball/{0}'.format(__version__)
)

setup(
    name='django-query-counter',
    version=__version__,
    author='Oleg Smedyuk',
    author_email='conformist.mw@gmail.com',
    description=('Debug tool to print sql queries count to the console'),
    install_requires=['tabulate'],
    license='MIT',
    keywords='django sql query count management commands',
    url=url,
    packages=[
        'query_counter',
    ],
    long_description=(
        'main feature of this project is to provide a decorator to give '
        'ability to check sql queries even inside management commands.'
    ),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Utilities',
    ],
)
