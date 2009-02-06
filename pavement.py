try:
    from paver.virtual import bootstrap
except :
    # minilib does not support bootstrap
    pass

from ConfigParser import ConfigParser as CP
from functools import partial
from paver.defaults import options, Bunch, task, sh, needs
from paver.runtime import debug, call_task
from pkg_resources import working_set, PathMetadata, Distribution, EggMetadata
from setuptools import find_packages
from setuptools.command.easy_install import PthDistributions
import distutils.debug
import os
import pkg_resources
import shutil
import sys
import zipimport

distutils.debug.DEBUG = True
