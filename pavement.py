try:
    from paver.virtual import bootstrap
except :
    # minilib does not support bootstrap
    pass

from ConfigParser import ConfigParser
from paver import setuputils
from paver.easy import *
from paver.easy import call_task
from paver.easy import call_task #debug,
from paver.easy import cmdopts #,consume_args
from paver.easy import path, sh, info
from paver.easy import task, options, Bunch
from paver.setuputils import setup
from paver.tasks import help, needs
from setuptools import find_packages
import os

setuputils.install_distutils_tasks()

version = "0.0"


setup(name='nunatak',
      version=version,
      description="OpenGeo Stack Builder",
      long_description="""
      Tools for building and managing an opengeo stack
      """,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='whit',
      author_email='whit@opengeo.org',
      url='http://www.opengeo.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      dependency_links=[],
      install_requires=["sphinx>=0.6.1",
                        "PasteDeploy",
                        "Paste",
                        "PasteScript",
                        "JSTools>=0.1.2",
                        ],
      entry_points="""
      """,
      )

curdir = os.path.abspath(os.curdir)
options(
    virtualenv=Bunch(script_name="build_stack",
                     packages_to_install=[],
                     paver_command_line="after_bootstrap"
                     ),
#    sphinx=Bunch(docroot="src/trunk/docsrc",
#                 builddir=path(curdir) / "built")
    )

@task
def auto():
    cp = ConfigParser()
    #@@ make an option??
    cp.read("stack-conf.cfg")
    options(config=cp)

@task
def build_stack():
    info("Not Implemented yet")
