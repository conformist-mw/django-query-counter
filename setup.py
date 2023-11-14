from setuptools import setup

from query_counter import __version__


def read_long_description():
    with open('README.md') as file:
        return file.read()


setup(
    name='django-query-counter',
    version=__version__,
    author='Oleg Smedyuk',
    author_email='oleg.smedyuk@gmail.com',
    description=('Debug tool to print sql queries count to the console'),
    install_requires=['tabulate'],
    license='MIT',
    keywords='django sql query count management commands',
    packages=[
        'query_counter',
    ],
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/conformist-mw/django-query-counter',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
