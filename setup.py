from setuptools import setup, find_packages
import sys, os

version = '0.0.3'

setup(name='vs2007',
      version=version,
      description="CUI for VS2007",
      long_description="""\
This is a command-line user interface for VisualStage2007.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='command-line',
      author='Yusuke Yachi',
      author_email='yyachi@misasa.okayama-u.ac.jp',
      url='http://dream.misasa.okayama-u.ac.jp',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
            "console_scripts": [
                  "vs2007-ctrl = vs2007.control:main",
                  "vs2007-api = vs2007.api:main",
            ]},
      )
