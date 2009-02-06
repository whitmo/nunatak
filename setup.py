from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='nunatak',
      version=version,
      description="a catch all for creating an environment for doing GIS work",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='GIS',
      author='whit',
      author_email='whit@opengeo.org',
      url='http://docs.geospiel.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
