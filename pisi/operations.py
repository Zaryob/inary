# Package Operations: install/remove/upgrade

import os

from config import config
from constants import const
from ui import ui
from purl import PUrl
import util

# single package operations

def remove(package_name):
    """Remove a single package"""
    from installdb import installdb
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
    removeScripts(package_name)

# TODO: repository'den okuma isi yas burada, bu degisecek
def install(pkg):
    url = PUrl(pkg)
    # Check if we are dealing with a remote file or a real path of
    # package filename. Otherwise we'll try installing a package from
    # the package repository.
    if url.isRemoteFile() or os.path.exists(url.uri):
        install_package(pkg)
    else:
        from os.path import join

        # TODO: tabii burada repodb falan kullanilmali cok inefficient
        (repo, index) = util.repo_index()

        # search pkg in index for it's presence in repository
        # TODO: normalde hicbir zaman boyle linear search yapilmamali
        # buyuk olabilecek listeler uzerinden
        for package in index.packages:
            if package.name == pkg:
                version = package.history[0].version
                release = package.history[0].release

                name = util.package_name(pkg, version, release)
                package_uri = join(repo, name[0], name)

                ui.info("Installing %s from repository %s\n" %(name, repo))
                install_package(package_uri)
                return
        ui.error("Package %s not found in the index file.\n" %pkg)

def install_package(pkg_location):
    from install import Installer
    Installer(pkg_location).install()

# deneme, don't remove ulan
class AtomicOperation(object):
    def __init__(self, package, ignore_dep = False):
        self.package = package
        self.ignore_dep = ignore_dep

    def run(self, package):
        "perform an atomic package operation"
        pass
