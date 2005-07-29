# Package Operations: install/remove/upgrade

import os

from config import config
from constants import const
from ui import ui
from purl import PUrl
import util, packagedb

# single package operations

def remove_single(package_name):
    """Remove a single package"""
    from installdb import installdb
    from packagedb import inst_packagedb
    from comariface import removeScripts

    #TODO: check dependencies

    ui.info('Removing package %s\n' % package_name)
    if not installdb.is_installed(package_name):
        raise Exception('Trying to remove nonexistent package '
                        + package_name)
    for fileinfo in installdb.files(package_name).list:
        fpath = os.path.join(config.destdir, fileinfo.path)
        # TODO: We have to store configuration files for futher
        # usage. Currently we'are doing it like rpm does, saving
        # with a prefix and leaving the user to edit it. In the future
        # we'll have a plan for these configuration files.
        if fileinfo.type == const.conf:
            os.rename(fpath, fpath+".pisi")
        else:
            os.unlink(fpath)
    installdb.remove(package_name)
    inst_packagedb.remove_package(package_name)
    removeScripts(package_name)

def install_single(pkg):
    """install a single package from URI or ID"""
    url = PUrl(pkg)
    # Check if we are dealing with a remote file or a real path of
    # package filename. Otherwise we'll try installing a package from
    # the package repository.
    if url.isRemoteFile() or os.path.exists(url.uri):
        install_single_file(pkg)
    else:
        install_single_name(pkg)

def install_single_file(pkg_location):
    """install a package file"""
    from install import Installer
    Installer(pkg_location).install()

def install_single_name(name):
    """install a single package from ID"""
    # find package in repository
    repo = packagedb.which_repo(name)
    if repo:
        pkg = packagedb.get_package(name)
        ui.info("Installing %s from repository %s\n" %(name, repo))
        ui.debug("Package URI: %s\n" % pkg.packageURI)
        install_single_uri(pkg.packageURI)
    else:
        ui.error("Package %s not found in the repository file.\n" % pkg)

# deneme, don't remove ulan
class AtomicOperation(object):
    def __init__(self, package, ignore_dep = False):
        self.package = package
        self.ignore_dep = ignore_dep

    def run(self, package):
        "perform an atomic package operation"
        pass
