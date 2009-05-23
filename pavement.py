from __future__ import with_statement

try:
    from paver.virtual import bootstrap
except :
    # minilib does not support bootstrap
    pass

from ConfigParser import ConfigParser, NoOptionError
from paver import setuputils
from paver.easy import *
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
import getpass
import pwd

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
                     packages_to_install=['supervisor',
                                          'tempita',
                                          'paste',
                                          'jstools'],
                     paver_command_line="after_bootstrap"
                     ),
#    sphinx=Bunch(docroot="src/trunk/docsrc",
#                 builddir=path(curdir) / "built")
    )

DEF_CONF = "stack-conf.cfg"
_c_base = 'proj', 'gdal', 'geos'

@task
def auto():
    env = os.environ.get('VIRTUAL_ENV')
    if env is None:
        env = path("./").abspath()
    cp = ConfigParser()
    # TODO: read stack-config from nunatak/resource dir
    # if no stack config exists
    
    #@@ make an option??
    cp.read(DEF_CONF)
    options(config=cp,
            env=env,
            conf_fp=DEF_CONF)

@task
@needs(['auto'])
def after_bootstrap():
    info("under construction")
    call_task("install_c_base")
    call_task("install_postgis")
    call_task("save_cfg")


@task
@needs(['auto'])
def save_cfg():
    options.config.write(open(options.conf_fp, 'w'))


@task
def build_stack():
    info("Not Implemented yet")


@task
@needs(['get_sources'])
def install_c_base():
    for pkg in _c_base:
        basic_install(pkg)


        
@task
@needs(['get_sources'])
def install_postgis():
    # @@ make configure optional?
    venv = options.env
    basic_install("readline")
    basic_install("postgres")
    pg_config = path(venv) / "bin/pg_config"
    basic_install("postgis", "--with-pgsql=%s" %pg_config)
    if  get_option(options.config, "installed", "gdal2") is None:
        basic_install("gdal", "--with-pg=%s" %pg_config, force=True)
        options.config.set("installed", "gdal2", True)
        call_task("save_cfg")
    pg_after_install()
        

# paver needs a "finish" autocall to write out the stack-config


ZIP = re.compile(r'.download/(.+)\.zip')

def zipfilename(dpath):
    # @@ maybe expand to get_filename
    return ZIP.match(dpath).groups()[0]

_irregulars = {'geoserver-1.7.4-bin':'geoserver-1.7.4'}

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
                filename = _irregulars.get(filename, filename)
                if not (src / filename).exists():
                    sh("unzip %s -d %s" %(tarball, src))
            else:
                source_path = tarball_unpack(tarball, src)
        else:
            # @@add svn checkup when needed
            pass
        options.config.set("sources", pkg, source_path.abspath())
    lpath = path("src/LICENSE.txt")
    if lpath.exists():
        lpath.remove()

_dirs = "src", "var", "etc", ".download", "var/logs"
        
@task
def dir_layout():
    env = path(options.env)
    for p in _dirs:
        if not (env / p).exists():
            os.mkdir(env / p)


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


def get_option(config, section, opt, default=None):
    try:
        return config.get(section, opt)
    except NoOptionError:
        return default


def basic_install(pkg, extra2="", config=None, clean=False, force=False):
    # use config.status to determine whether to rerun?
    venv = options.env
    if config is None:
        config = options.config
    src = path(config.get('sources', pkg))
    extra = get_option(config, 'install_options', pkg, "")
    if force is True:
        config.remove_option('installed', pkg)
    if get_option(config, "installed", pkg) is None:
        with pushd(src) as root:
            sh("configure LDFLAGS=-L%s CPPFLAGS=-I%s --prefix=%s %s %s" %(str(path(venv) / 'lib'), str(path(venv) / 'include'), venv, extra, extra2))
            if clean:
                sh("make clean")
            sh("make")
            sh("make install")
            config.set('installed', pkg, True)
            call_task("save_cfg")

        
def add_pg_user():
    if sys.platform == 'darwin':
        info("osx user add not implemented yet")
        # http://osxdaily.com/2007/10/29/how-to-add-a-user-from-the-os-x-command-line-works-with-leopard/
##         Create a new entry in the local (/) domain under the category /users.
##         dscl / -create /Users/toddharris

##         Create and set the shell property to bash.
##         dscl / -create /Users/toddharris UserShell /bin/bash

##         Create and set the user's full name.
##         dscl / -create /Users/toddharris RealName "Dr. Todd Harris"

##         Create and set the users ID.
##         dscl / -create /Users/toddharris UniqueID 503

##         Create and set the users group ID property.
##         dscl / -create /Users/toddharris PrimaryGroupID 1000

##         Create and set the user home directory.
##         dscl / -create /Users/toddharris NFSHomeDirectory /Local/Users/toddharris

##         Set the password.
##         dscl / -passwd /Users/toddharris PASSWORD
    else:
        info("*nix user add not implemented yet")
    return pwd.getpwnam('postgres')[2]

def pg_after_install():
    # set up postgres user
    try:
        pguserid = pwd.getpwnam('postgres')[2]
    except KeyError:
        pguserid = add_pg_user()
    vardir = path(options.env) / 'var'
    pgdata = vardir / 'pgdata'
    if not pgdata.exists():
        try:
            pgdata.mkdir()
            subprocess.call("sudo chown postgres:postgres %s" %pgdata.abspath(), shell=True)
            subprocess.call("sudo -u postgres bin/initdb -D %s" %pgdata.abspath(), shell=True)
        except :
            pgdata.rmdir()
            raise
    
