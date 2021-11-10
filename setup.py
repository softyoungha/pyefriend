# -*- coding:utf-8 -*-
from setuptools import setup
from pip._internal.req import parse_requirements

install_requires = [
                       str(r.requirement)
                       for r in parse_requirements('requirements.txt', session='hack')
                   ] + [
                       'pywin32 >= 1.0 ; platform_system=="Windows"',
                   ]

setup(install_requires=install_requires)
