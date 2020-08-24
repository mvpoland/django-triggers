#!/usr/bin/env python
from setuptools import setup, find_packages
import djtriggers

setup(
    name="django-triggers",
    version=djtriggers.__version__,
    url='https://github.com/citylive/django-triggers',
    license='BSD',
    description="Framework to create and process triggers.",
    long_description=open('README.md', 'r').read(),
    author='Olivier Sels, City Live nv',
    packages=find_packages(),
    install_requires=[
        "future"
    ],
    zip_safe=False,  # Don't create egg files, Django cannot find templates in egg files.
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
