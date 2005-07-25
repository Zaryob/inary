# -*- coding: utf-8 -*-
# Package install operation
# Author:  Eray Ozkural <eray@uludag.org.tr>

import os

from specfile import *
from package import Package
from config import config
from constants import const
from ui import ui
from installdb import installdb
from packagedb import packagedb, inst_packagedb
import dependency
from metadata import MetaData
import comariface
import operations
#import conflicts

class InstallError(Exception):
    pass

class Installer:
    "Installer class, provides install routines for pisi packages"

    def __init__(self, package_fname):
        "initialize from a file name"
        self.package = Package(package_fname)
        self.package.read()
        self.metadata = self.package.metadata
        self.files = self.package.files

    def install(self):
        "entry point"
        self.pkginfo = self.metadata.package
        self.check_requirements()
        self.check_relations()
        self.reinstall()
        self.extractInstall()
        self.storePisiFiles()
        self.registerCOMARScripts()
        self.update_databases()

    def extractInstall(self):
        "unzip package in place"

        ui.info('Extracting files\n')
        self.package.extract_dir_flat('install', config.destdir)
 
    def storePisiFiles(self):
        """put files.xml, metadata.xml, actions.py and COMAR scripts
        somewhere in the file system. We'll need these in future..."""

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
        "register COMAR scripts"

        for pcomar in self.metadata.package.providesComar:
            scriptPath = os.path.join(self.package.comar_dir(),pcomar.script)
            ui.info("Registering COMAR script %s\n" % pcomar.script)
            ret = comariface.registerScript(pcomar.om,
                                            self.metadata.package.name,
                                            scriptPath)
            if not ret:
                ui.error("registerScript failed. Be sure that comard is running!\n")

    def check_requirements(self):
        """check system requirements"""
        
        #TODO: IS THERE ENOUGH SPACE?
        # what to do if / is split into /usr, /var, etc.
        pass

    def check_relations(self):
        # check if package is in database
        # TODO: when repodb comes alive, this will put it into 3rd
        # party packagedb
        if not packagedb.has_package(self.pkginfo.name):
            packagedb.add_package(self.pkginfo) # terrible solution it seems
    
        # check conflicts
        for pkg in self.metadata.package.conflicts:
            if installdb.has_package(self.pkginfo):
                raise InstallError("Package conflicts " + pkg)
    
        # check dependencies
        if not dependency.installable(self.pkginfo.name):
            ui.error('Dependencies for ' + self.pkginfo.name +
                     ' not satisfied\n')
            raise InstallError("Package not installable")

    def reinstall(self):
        "check reinstall, confirm action, and remove package if reinstall"

        pkg = self.pkginfo
        
        if installdb.is_installed(pkg.name): # is this a reinstallation?
            (iversion, irelease) = installdb.get_version(pkg.name)

            if pkg.version == iversion and pkg.release == irelease:
                if not ui.confirm('Re-install same version package?'):
                    raise InstallError('Package re-install declined')
            else:
                upgrade = False
                # is this an upgrade?
                # determine and report the kind of upgrade: version, release, build
                if pkg.version > iversion:
                    ui.info('Upgrading to new upstream version')
                    upgrade = True
                elif pkg.release > irelease:
                    ui.info('Upgrading to new distribution release')
                    upgrade = True

                # is this a downgrade? confirm this action.
                if not upgrade:
                    if pkg.version < iversion:
                        x = 'Downgrade to old upstream version?'
                    elif pkg.release < irelease:
                        x = 'Downgrade to old distribution release?'
                    if not ui.confirm(x):
                        raise InstallError('Package downgrade declined')

            # remove old package then
            operations.remove_single(pkg.name)

    def update_databases(self):
        "update databases"

        # installdb
        installdb.install(self.metadata.package.name,
                          self.metadata.package.version,
                          self.metadata.package.release)

        # installed packages
        inst_packagedb.add_package(self.pkginfo)
