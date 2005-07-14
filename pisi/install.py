# -*- coding: utf-8 -*-
# Package install operation
# Author:  Eray Ozkural <eray@uludag.org.tr>

import os

from specfile import *
from package import Package
from files import Files
import util
from config import config
from ui import ui
from installdb import installdb
from packagedb import packagedb
import dependency
from metadata import MetaData
#import conflicts

##TODO: Caglar'in onerisi uzerine.
##bunu PisiBuild gibi class yapalim. Asagida yazdigim
##gibi bir test edip nerelere extend edecek ama gorelim
##lutfen. daha hic calismadi bile. :/

class InstallError(Exception):
    pass

from os.path import join, exists

def get_pkg_info(package_fn):
    package = Package(package_fn, 'r')
    # extract control files
    util.clean_dir(config.install_dir())
    package.extract_PISI_files(config.install_dir())

    # verify package

    # check if we have all required files
    if not exists(join(config.install_dir(), 'metadata.xml')):
        raise InstallError('metadata.xml missing')
    if not exists(join(config.install_dir(), 'files.xml')):
        raise InstallError('files.xml missing')
    
    metadata = MetaData()
    metadata.read(join(config.install_dir(), 'metadata.xml'))

    files = Files()
    files.read(join(config.install_dir(), 'files.xml'))

    return metadata, files


def remove(package_name):
    """Remove a goddamn package"""
    ui.info('Removing package ' + package_name)
    if not installdb.is_installed(package_name):
        raise InstallError('Trying to remove nonexistent package '
                           + package_name)
    for fileinfo in installdb.files(package_name):
        os.unlink(fileinfo.path)
    installdb.remove(package_name)

def install(package_fn):

    metadata, files = get_pkg_info(package_fn)
    
    # check package semantics
    if not metadata.verify():
        raise InstallError("MetaData format wrong")

    # check file system requirements
    # what to do if / is split into /usr, /var, etc.?

    package = metadata.package

    # check if package is in database
    if not packagedb.has_package(package.name):
        packagedb.add_package(package) # terrible solution it seems
    
    # check conflicts
    for pkg in metadata.package.conflicts:
        if installdb.has_package(package):
            raise InstallError("Package conflicts " + pkg)
    
    # check dependencies
    if not dependency.installable(package.name):
        raise InstallError("Package not installable")

    #TODO:
    if installdb.is_installed(package.name): # is this a reinstallation?

        (iversion, irelease) = installdb.get_version(package.name)

        if package.version == iversion and package.release == irelease:
            if not ui.confirm('Re-install same version package?'):
                raise InstallError('Package re-install declined')

        upgrade = False
        # is this an upgrade?
        # determine and report the kind of upgrade: version, release, build
        if package.version > iversion:
            ui.info('Upgrading to new upstream version')
            upgrade = True
        elif package.release > irelease:
            ui.info('Upgrading to new distribution release')
            upgrade = True

        # is this a downgrade? confirm this action.
        if not upgrade:
            if package.version < iversion:
                x = 'Downgrade to old upstream version?'
            elif package.release < irelease:
                x = 'Downgrade to old distribution release?'
            if not ui.confirm(x):
                raise InstallError('Package downgrade declined')

        # remove old package then
        remove(package.name)

    # unzip package in place
    ui.info('Extracting files\n')
    package.extract_dir_flat('install', config.destdir)

    # TODO: put files.xml, metadata.xml, actions.py and COMAR scripts
    # somewhere in the file system. We'll need these in future...

    # TODO: register COMAR scripts
    # something like the below?
    # import comariface
    # for comar int metadata.package.providesComar:
    #     comariface.register(comar.om, comar.script)

    # update databases

    # installdb
    installdb.install(metadata.package.name,
                      metadata.package.version,
                      metadata.package.release,
                      os.path.join(config.install_dir(), 'files.xml'))
