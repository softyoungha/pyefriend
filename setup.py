#-*- coding:utf-8 -*-
from setuptools import setup, find_packages
from pip._internal.req import parse_requirements

install_requires = [
      str(r.requirement)
      for r in parse_requirements('requirements.txt', session='hack')
]

setup(name='pyefriend',
      version='1.0',
      author='Youngha Park',
      author_email='proyoungha@naver.com',
      install_requires=install_requires,
      url='https://softyoungha.github.io/',
      license='MIT',
      description="Python API link to 'efriend expert'",
      long_description=open('README.md', encoding='utf-8').read(),
      long_description_content_type='text/markdown',
      keywords=['pyefriend', 'rebalancing', 'efriend-expert'],
      py_modules=['pyefriend', 'rebalancing'],
      python_requires='>=3',
      packages=find_packages(include=['pyefriend',
                                      'rebalancing',
                                      'rebalancing.*']),
      package_data={
            'rebalancing': [
                  'config.template.yml',
                  'data/*.csv',
            ]},
      entry_points={
            'console_scripts': [
                  'rebalancing=rebalancing.__main__:main',
            ],
      })
