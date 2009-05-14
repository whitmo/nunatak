from __future__ import with_statement

try:
    from paver.virtual import bootstrap
except :
    # minilib does not support bootstrap
    pass

from ConfigParser import ConfigParser, NoOptionError
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
import os
import re
import shutil
import subprocess

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

def tarball_unpack(fpath, dest, overwrite=False):
    """
    Dumbly unpack tarballs and zips

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

    dest_folder = dest / filename.split(".tar.")[0]
    if not dest_folder.exists() and overwrite:
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
    return dest_folder

def basic_install(pkg, extra2="", config=None, clean=False):
    venv = os.environ['VIRTUAL_ENV']
    if config is None:
        config = options.config
    src = path(config.get('sources', pkg))
    try:
        extra = config.get('install_options', pkg)
    except NoOptionError:
        extra = ""
    with pushd(src) as root:
        sh("configure LDFLAGS=-L%s CPPFLAGS=-I%s --prefix=%s %s %s" %(str(path(venv) / 'lib'), str(path(venv) / 'include'), venv, extra, extra2))
        if clean:
            sh("make clean")
        sh("make")
        sh("make install")

@task
@needs(['get_sources'])
def install_c_base():
    for pkg in 'proj', 'gdal', 'geos':
        basic_install(pkg)

@task
@needs(['get_sources'])
def install_postgis():
    # @@ make configure optional?
    venv = os.environ['VIRTUAL_ENV']
    basic_install("readline")
    basic_install("postgres")
    pg_config = path(venv) / "bin/pg_config"
    basic_install("postgis", "--with-pgsql=%s" %pg_config)
    basic_install("gdal", "--with-pg=%s" %pg_config) 

# paver needs a "finish" autocall to write out the stack-config


ZIP = re.compile(r'.download/(.+)\.zip')

def zipfilename(dpath):
    # @@ maybe expand to get_filename
    return ZIP.match(dpath).groups()[0]


@task
@needs(['dir_layout'])
def get_sources():
    for pkg in options.config.options("urls"):
        url = options.config.get("urls", pkg)
        src = path("./src")
        if url.startswith("ftp") or url.startswith("http"):
            tarball = download(url)
            if tarball.endswith("zip"):
                filename = zipfilename(tarball)
                if not (src / filename).exists():
                    sh("unzip %s -d %s" %(tarball, src))
            else:
                source_path = tarball_unpack(tarball, src)
        else:
            # @@add svn checkup when needed
            pass
        options.config.set("sources", pkg, str(source_path))
    lpath = path("src/LICENSE.txt")
    if lpath.exists():
        lpath.remove()
        
@task
def dir_layout():
    env = path(options.env)
    for p in "src", "var", "etc", ".download",:
        if not (env / p).exists():
            os.mkdir(env / p)



