import os

from config import config
from constants import const
from ui import ui
from purl import PUrl

# all package operation interfaces are here

def remove(package_name):
    """Remove a goddamn package"""
    from installdb import installdb

    ui.info('Removing package %s\n' % package_name)
    if not installdb.is_installed(package_name):
        raise Exception('Trying to remove nonexistent package '
                        + package_name)
    for fileinfo in installdb.files(package_name).list:
        os.unlink( os.path.join(config.destdir, fileinfo.path) )
    installdb.remove(package_name)


def install(pkg_location):
    from install import Installer

    url = PUrl(pkg_location)
    if url.isRemoteFile():
        pass # bunu simdilik bosverelim, once bir calissin :)

    i = Installer(url.uri)
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
    index.write('pisi-index.xml')
    ui.info('* Index file written\n')

def updatedb(indexfile):
    from index import Index

    ui.info('* Updating DB from index file: %s\n' % indexfile)
    index = Index()
    index.read(indexfile)
    index.update_db()
    ui.info('* Package db updated.\n')
