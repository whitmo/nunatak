from __future__ import with_statement

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
from paver.easy import path, sh, info, pushd
from paver.easy import task, options, Bunch
from paver.setuputils import setup
from paver.tasks import help, needs
from setuptools import find_packages
import subprocess
import os
import shutil

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
    env = os.environ['VIRTUAL_ENV']
    cp = ConfigParser()
    #@@ make an option??
    cp.read("stack-conf.cfg")
    options(config=cp,
            env=env)

@task
def build_stack():
    info("Not Implemented yet")



def download(url, dest=".download"):
    filename = url.split("/")[-1]
    ppath = path(dest)

    fpath = ppath / filename
    if not (ppath / filename).exists():
        oldnames = set(ppath.listdir())
        with pushd(ppath) as old_dir:
            sh("wget %s" %url)
    return fpath

def tarball_unpack(fpath, dest):
    """
    Dumbly unpack tarballs

    fpath --
       filepath of tarball

    dest --
       folder to upack into

    @return
        name of folder created by unpacking
    """
    dest = path(dest)
    filename = fpath.split("/")[-1]
    newfile = dest / filename
    old = set(os.listdir(dest))
    shutil.copyfile(str(fpath), str(newfile))
    with pushd(dest):
        catcmd = "zcat"
        if filename.endswith("bz2") or filename.endswith("bz"):
            catcmd = "bzcat"
        cat = subprocess.Popen([catcmd, filename], stdout=subprocess.PIPE)
        untar = subprocess.Popen(["tar", "-xf", "-"], stdin=cat.stdout, stdout=subprocess.PIPE)
        info("Unpacking %s" %filename)
        untar.communicate()
    os.remove(newfile)
    return dest / filename.split(".tar.")[0]

# paver needs a "finish" to right out the stack-config

@task
@needs(['dir_layout'])
def get_sources():
    for pkg in options.config.options("urls"):
        url = options.config.get("urls", pkg)
        if url.startswith("ftp") or url.startswith("http"):
            tarball = download(url)
            source_path = tarball_unpack(tarball, "src")
        else:
            # @@add svn checkup when needed
            pass
        options.config.set("sources", pkg, str(source_path))
        
@task
def dir_layout():
    env = path(options.env)
    for p in "src", "var", "etc", ".download",:
        if not (env / p).exists():
            os.mkdir(env / p)



