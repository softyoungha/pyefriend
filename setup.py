#-*- coding:utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
      # default
      'pyyaml==6.0',
      'requests==2.26.0',

      # Need python 32-bit and administrator
      'PyQt5==5.15.6',

      # visualization
      'ipython==7.29.0',
      'jupyter==1.0.0',
      'notebook==6.4.5',
      'pywinpty<1,>=0.5',

      # sqlalchemy
      'sqlalchemy==1.4.26',
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
                  'rebalancing2=rebalancing:main',
            ],
      })
