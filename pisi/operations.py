import os

from config import config
from constants import const
from ui import ui
from package import Package
from installdb import installdb
from packagedb import packagedb
from purl import PUrl

# all package operation interfaces are here

def remove(package_name):
    """Remove a goddamn package"""
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
    package = Package(package_name)
    package.read()
    return package.metadata, package.files


