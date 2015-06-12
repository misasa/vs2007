from setuptools import setup, find_packages
import sys, os
from vs2007._version import __version__ as VERSION

#version = '0.1.1'

setup(name='vs2007',
      version=VERSION,
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
                  "vs = vs2007.control:main",
                  "vs-api = vs2007.api:main",
            ]},
      )
