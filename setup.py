# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from quiz import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='django-quiz',
    version=".".join(map(str, VERSION)),
    author=u'François Chapuis',
    author_email='afnarel@gmail.com',
    packages=find_packages(),
    url='https://github.com/Afnarel/django-quiz',
    include_package_data=True,
    license='MIT licence, see LICENCE.txt',
    description='Quiz app for Django',
    long_description=readme,
    zip_safe=False,
)
