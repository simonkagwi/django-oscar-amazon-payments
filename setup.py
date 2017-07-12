#!/usr/bin/env python
from setuptools import setup, find_packages
import os
PAR_DIR = os.path.dirname(__file__)

setup(
    name='django-oscar-amazon-payments',
    version="0.1",
    url='https://github.com/simonkagwe/django-oscar-amazon-payments',
    author="Simon Kagwi",
    author_email="simonkagwe@yahoo.com",
    description=(
        "This package provides integration between django-oscar and "
        "Amazon Payments (Login and Pay with Amazon)."),
    long_description=open(os.path.join(PAR_DIR, 'README.rst')).read(),
    keywords="Amazon Payments, Oscar, Django",
    license=open(os.path.join(PAR_DIR, 'LICENSE')).read(),
    platforms=['linux'],
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    include_package_data=True,
    install_requires=[
        'requests',
        'beautifulsoup4',
        'lxml'],
    extras_require={
        'oscar': ["Django==1.6", "django-oscar==0.7.3",
                  "django-compressor==1.6", "django-haystack==2.1"]
    },
    setup_requires=['pytest-runner'],
    tests_require=[
        "pytest==2.6.4",
        "pytest-cov==1.7.0",
        "pytest-django==2.8.0",
        'mock==1.0.1',
    ],
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
