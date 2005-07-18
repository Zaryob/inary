# -*- coding: utf-8 -*-
# Package install operation
# Author:  Eray Ozkural <eray@uludag.org.tr>

import os

from specfile import *
from package import Package
from files import Files
import util
from config import config
from constants import const
from ui import ui
from installdb import installdb
from packagedb import packagedb
import dependency
from metadata import MetaData
import comariface
#import conflicts

class InstallError(Exception):
    pass

class Installer:
    "Installer class, provides install routines for pisi packages"
    def __init__(self, package_fname):
        self.package = Package(package_fname)
        self.package.read_info()
        self.metadata = self.package.metadata
        self.files = self.package.files

    def extractInstall(self):
        ui.info('Extracting files\n')
        self.package.extract_dir_flat('install', config.destdir)
    
    def storePisiFiles(self):
        # put files.xml, metadata.xml, actions.py and COMAR scripts
        # somewhere in the file system. We'll need these in future...

        ui.info('Storing %s\n' % const.files_xml)
        self.package.extract_file(const.files_xml, self.package.pkg_dir())

        ui.info('Storing %s\n' % const.metadata_xml)
        self.package.extract_file(const.metadata_xml, self.package.pkg_dir())

        for pcomar in self.metadata.package.providesComar:
            fpath = os.path.join(const.comar_dir, pcomar.script)
            # comar prefix is added to the pkg_dir while extracting comar
            # script file. so we'll use pkg_dir as destination.
            ui.info('Storing %s\n' % fpath)
            self.package.extract_file(fpath, self.package.pkg_dir())

    def registerCOMARScripts(self):
        # register COMAR scripts
        for pcomar in self.metadata.package.providesComar:
            scriptPath = os.path.join(self.package.comar_dir(),pcomar.script)
            ui.info("Registering COMAR script %s\n" % pcomar.script)
            ret = comariface.registerScript(pcomar.om,
                                            self.metadata.package.name,
                                            scriptPath)
            if not ret:
                ui.error("registerScript failed. Be sure that comard is running!\n")


    def install(self):

        # check file system requirements
        # what to do if / is split into /usr, /var, etc.?

        pkginfo = self.metadata.package

        # check if package is in database
        if not packagedb.has_package(pkginfo.name):
            packagedb.add_package(pkginfo) # terrible solution it seems
    
        # check conflicts
        for pkg in self.metadata.package.conflicts:
            if installdb.has_package(pkginfo):
                raise InstallError("Package conflicts " + pkg)
    
        # check dependencies
        if not dependency.installable(pkginfo.name):
            ui.error('Dependencies for ' + pkginfo.name +
                     ' not satisfied\n')
            
            raise InstallError("Package not installable")

        #TODO:
        if installdb.is_installed(pkginfo.name): # is this a reinstallation?
            (iversion, irelease) = installdb.get_version(pkginfo.name)

            if pkginfo.version == iversion and pkginfo.release == irelease:
                if not ui.confirm('Re-install same version package?'):
                    raise InstallError('Package re-install declined')

            upgrade = False
            # is this an upgrade?
            # determine and report the kind of upgrade: version, release, build
            if pkginfo.version > iversion:
                ui.info('Upgrading to new upstream version')
                upgrade = True
            elif pkginfo.release > irelease:
                ui.info('Upgrading to new distribution release')
                upgrade = True

            # is this a downgrade? confirm this action.
            if not upgrade:
                if pkginfo.version < iversion:
                    x = 'Downgrade to old upstream version?'
                elif pkginfo.release < irelease:
                    x = 'Downgrade to old distribution release?'
                if not ui.confirm(x):
                    raise InstallError('Package downgrade declined')

            # remove old package then
            remove(pkginfo.name)

        # unzip package in place
        self.extractInstall()

        # store files.xml, metadata.xml and comar scripts for further usage
        self.storePisiFiles()

        # register comar scripts
        self.registerCOMARScripts()

        # update databases

        # installdb
        installdb.install(self.metadata.package.name,
                          self.metadata.package.version,
                          self.metadata.package.release,
                          os.path.join(self.package.pkg_dir(), 'files.xml'))
