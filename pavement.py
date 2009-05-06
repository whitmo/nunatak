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
