# -*- coding:utf-8 -*-
""" 설정 파일은 모두 setup.cfg에 설정 """
from setuptools import setup
from pip._internal.req import parse_requirements

install_requires = [
    str(r.requirement)
    for r in parse_requirements('requirements.txt', session='hack')
]

setup(install_requires=install_requires)
