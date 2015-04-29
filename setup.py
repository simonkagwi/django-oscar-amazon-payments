#!/usr/bin/env python
from setuptools import setup, find_packages

from amazon_payments import VERSION


setup(
    name='django-oscar-amazon-payments',
    version=VERSION,
    url='https://github.com/simonkagwe/django-oscar-amazon-payments',
    author="Simon Kagwi",
    author_email="simonkagwe@yahoo.com",
    description=(
        "This package provides integration between django-oscar and "
        "Amazon Payments (Login and Pay with Amazon)."),
    long_description=open('README.rst').read(),
    keywords="Amazon Payments, Oscar, Django",
    license=open('LICENSE').read(),
    platforms=['linux'],
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    include_package_data=True,
    install_requires=[
        'requests',
        'beautifulsoup4',
        'lxml'],
    extras_require={
        'oscar': ["django-oscar>=0.7"]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Other/Nonlisted Topic'],
)
