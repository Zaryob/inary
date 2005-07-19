import os

from config import config
from constants import const
from ui import ui
from purl import PUrl
import util


# all package operation interfaces are here

def remove(package_name):
    """Remove a goddamn package"""
    from installdb import installdb
    from comariface import removeScripts

    ui.info('Removing package %s\n' % package_name)
    if not installdb.is_installed(package_name):
        raise Exception('Trying to remove nonexistent package '
                        + package_name)
    for fileinfo in installdb.files(package_name).list:
        os.unlink( os.path.join(config.destdir, fileinfo.path) )
    installdb.remove(package_name)
    removeScripts(package_name)

def install(pkg):
    url = PUrl(pkg)
    # Check if we are dealing with a remote file or a real path of
    # package filename. Otherwise we'll try installing a package from
    # the package repository.
    if url.isRemoteFile() or os.path.exists(url.uri):
        install_package(pkg)
    else:
        from os.path import join

        (repo, index) = util.repo_index()

        # search pkg in index for it's presence in repository
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

    i = Installer(pkg_location)
    i.install()


def info(package_name):
    from package import Package

    package = Package(package_name)
    package.read()
    return package.metadata, package.files


def index(repo_dir = '.'):
    from index import Index

    ui.info('* Building index of PISI files under %s\n' % repo_dir)
    index = Index()
    index.index(repo_dir)
    index.write(const.pisi_index)
    ui.info('* Index file written\n')

def updatedb(indexfile = None):
    from index import Index

    if not indexfile:
        repos_path = config.values.repos.default
        indexfile = os.path.join(repos_path, const.pisi_index)

    ui.info('* Updating DB from index file: %s\n' % indexfile)
    index = Index()
    index.read(indexfile)
    index.update_db()
    ui.info('* Package db updated.\n')


def build(pspecfile, authInfo=None):
    from build import PisiBuild

    url = PUrl(pspecfile)
    if url.isRemoteFile():
        from sourcefetcher import SourceFetcher
        fs = SourceFetcher(url, authInfo)
        url.uri = fs.fetch_all()

    pb = PisiBuild(url.uri)
    pb.build()
