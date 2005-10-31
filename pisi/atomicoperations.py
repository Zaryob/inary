# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Package install operation

# Author:  Eray Ozkural <eray@uludag.org.tr>


# for python 2.3 compatibility
import sys
ver = sys.version_info
if ver[0] <= 2 and ver[1] < 4:
    from sets import Set as set

import os

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi

import pisi.context as ctx
import pisi.packagedb as packagedb
import pisi.dependency as dependency
import pisi.util as util
from pisi.specfile import *
from pisi.package import Package
from pisi.metadata import MetaData
from pisi.uri import URI
#import conflicts

class Error(pisi.Error):
    pass

# single package operations

class AtomicOperation(object):

    def __init__(self, ignore_dep = None):
        #self.package = package
        if ignore_dep==None:
            self.ignore_dep = ctx.config.get_option('ignore_dependency')
        else:
            self.ignore_dep = ignore_dep

    def run(self, package):
        "perform an atomic package operation"
        pass


class Install(AtomicOperation):
    "Install class, provides install routines for pisi packages"

    def __init__(self, package_fname, ignore_dep = None):
        "initialize from a file name"
        super(Install, self).__init__(ignore_dep)
        self.package = Package(package_fname)
        self.package.read()
        self.metadata = self.package.metadata
        self.files = self.package.files
        self.pkginfo = self.metadata.package

    def install(self, ask_reinstall = True):
        "entry point"
        ctx.ui.info(_('Installing %s, version %s, release %s, build %s') %
                (self.pkginfo.name, self.pkginfo.version,
                 self.pkginfo.release, self.pkginfo.build))
        self.ask_reinstall = ask_reinstall
        self.check_requirements()
        self.check_relations()
        self.check_reinstall()
        self.extract_install()
        self.store_pisi_files()
        if ctx.comar:
            import pisi.comariface as comariface
            self.register_comar_scripts()
            if not ctx.config.options.postpone_postinstall:
                comariface.run_postinstall(self.pkginfo.name)
        self.update_databases()
        self.update_environment()
                        
    def check_requirements(self):
        """check system requirements"""
        #TODO: IS THERE ENOUGH SPACE?
        # what to do if / is split into /usr, /var, etc.
        pass

    def check_relations(self):
        # check conflicts
        for pkg in self.metadata.package.conflicts:
            if ctx.installdb.is_installed(self.pkginfo):
                raise Error(_("Package conflicts %s") % pkg)

        # check dependencies
        if not ctx.config.get_option('ignore_dependency'):
            if not self.pkginfo.installable():
                ctx.ui.error(_('Dependencies for %s not satisfied') %
                             self.pkginfo.name)
                raise Error(_("Package not installable"))

        # check if package is in database
        # If it is not, put it into 3rd party packagedb
        if not packagedb.has_package(self.pkginfo.name):
            db = packagedb.thirdparty_packagedb
            db.add_package(self.pkginfo)

    def check_reinstall(self):
        "check reinstall, confirm action, and schedule reinstall"

        pkg = self.pkginfo

        self.reinstall = False
        if ctx.installdb.is_installed(pkg.name): # is this a reinstallation?
            (iversion, irelease, ibuild) = ctx.installdb.get_version(pkg.name)

            # determine if same version
            same_ver = False
            ignore_build = ctx.config.options and ctx.config.options.ignore_build_no
            if (not ibuild) or (not pkg.build) or ignore_build:
                # we don't look at builds to compare two package versions
                if pkg.version == iversion and pkg.release == irelease:
                    same_ver = True
            else:
                if pkg.build == ibuild:
                    same_ver = True

            if same_ver:
                if self.ask_reinstall:
                    if not ctx.ui.confirm(_('Re-install same version package?')):
                        raise Error(_('Package re-install declined'))
            else:
                upgrade = False
                # is this an upgrade?
                # determine and report the kind of upgrade: version, release, build
                if pkg.version > iversion:
                    ctx.ui.info(_('Upgrading to new upstream version'))
                    upgrade = True
                elif pkg.release > irelease:
                    ctx.ui.info(_('Upgrading to new distribution release'))
                    upgrade = True
                elif ((not ignore_build) and ibuild and pkg.build
                       and pkg.build > ibuild):
                    ctx.ui.info(_('Upgrading to new distribution build'))
                    upgrade = True

                # is this a downgrade? confirm this action.
                if self.ask_reinstall and (not upgrade):
                    if pkg.version < iversion:
                        x = _('Downgrade to old upstream version?')
                    elif pkg.release < irelease:
                        x = _('Downgrade to old distribution release?')
                    else:
                        x = _('Downgrade to old distribution build?')
                    if not ctx.ui.confirm(x):
                        raise Error(_('Package downgrade declined'))

            # schedule for reinstall
            self.old_files = ctx.installdb.files(pkg.name)
            self.reinstall = True
            Remove(pkg.name).run_preremove()

    def extract_install(self):
        "unzip package in place"

        ctx.ui.info(_('Extracting files'))
        self.package.extract_dir_flat('install', ctx.config.dest_dir())

        if self.reinstall:
            # remove left over files
            new = set(map(lambda x: str(x.path), self.files.list))
            old = set(map(lambda x: str(x.path), self.old_files.list))
            leftover = old - new
            old_fileinfo = {}
            for fileinfo in self.old_files.list:
                old_fileinfo[str(fileinfo.path)] = fileinfo
            for path in leftover:
                Remove.remove_file( old_fileinfo[path] )

    def store_pisi_files(self):
        """put files.xml, metadata.xml, actions.py and COMAR scripts
        somewhere in the file system. We'll need these in future..."""

        ctx.ui.info(_('Storing %s, ') % ctx.const.files_xml)
        self.package.extract_file(ctx.const.files_xml, self.package.pkg_dir())

        ctx.ui.info(_('Storing %s.') % ctx.const.metadata_xml)
        self.package.extract_file(ctx.const.metadata_xml, self.package.pkg_dir())

        for pcomar in self.metadata.package.providesComar:
            fpath = os.path.join(ctx.const.comar_dir, pcomar.script)
            # comar prefix is added to the pkg_dir while extracting comar
            # script file. so we'll use pkg_dir as destination.
            ctx.ui.info(_('Storing %s') % fpath)
            self.package.extract_file(fpath, self.package.pkg_dir())

    def register_comar_scripts(self):
        "register COMAR scripts"

        for pcomar in self.metadata.package.providesComar:
            scriptPath = os.path.join(self.package.comar_dir(),pcomar.script)
            import pisi.comariface
            pisi.comariface.register(pcomar, self.metadata.package.name,
                                     scriptPath)

    def update_databases(self):
        "update databases"

        if self.reinstall:
            Remove(self.metadata.package.name).remove_db()

        # installdb
        ctx.installdb.install(self.metadata.package.name,
                          self.metadata.package.version,
                          self.metadata.package.release,
                          self.metadata.package.build,
                          self.metadata.package.distribution)

        # filesdb
        ctx.filesdb.add_files(self.metadata.package.name, self.files)

        # installed packages
        packagedb.inst_packagedb.add_package(self.pkginfo)

    def update_environment(self):
        # check if we have any shared objects or anything under
        # /etc/env.d
        shared = False
        for x in self.files.list:
            if x.path.endswith('.so') or x.path.startswith('/etc/env.d'):
                shared = True
                break
        if shared:
            ctx.ui.info("Regenerating /etc/ld.so.cache...")
            util.env_update()


def install_single(pkg, upgrade = False):
    """install a single package from URI or ID"""
    url = URI(pkg)
    # Check if we are dealing with a remote file or a real path of
    # package filename. Otherwise we'll try installing a package from
    # the package repository.
    if url.is_remote_file() or os.path.exists(url.uri):
        install_single_file(pkg, upgrade)
    else:
        install_single_name(pkg, upgrade)

# FIXME: Here and elsewhere pkg_location must be a URI
def install_single_file(pkg_location, upgrade = False):
    """install a package file"""
    Install(pkg_location).install(not upgrade)

def install_single_name(name, upgrade = False):
    """install a single package from ID"""
    # find package in repository
    repo = packagedb.which_repo(name)
    if repo:
        repo = ctx.repodb.get_repo(repo)
        pkg = packagedb.get_package(name)

        # FIXME: let pkg.packageURI be stored as URI type rather than string
        pkg_uri = URI(pkg.packageURI)
        if pkg_uri.is_absolute_path():
            pkg_path = str(pkg.packageURI)
        else:
            pkg_path = os.path.join(os.path.dirname(repo.indexuri.get_uri()),
                                    str(pkg_uri.path()))

        ctx.ui.debug(_("Package URI: %s") % pkg_path)

        # Package will handle remote file for us!
        install_single_file(pkg_path, upgrade)
    else:
        raise Error(_("Package %s not found in any active repository.") % name)


class Remove(AtomicOperation):
    
    def __init__(self, package_name, ignore_dep = None):
        super(Remove, self).__init__(ignore_dep)
        self.package_name = package_name
        
    def run(self):
        """Remove a single package"""
        inst_packagedb = packagedb.inst_packagedb
        self.package = packagedb.get_package(self.package_name)
       
        ctx.ui.info(_('Removing package %s') % self.package_name)
        if not ctx.installdb.is_installed(self.package_name):
            raise Exception(_('Trying to remove nonexistent package ')
                            + self.package_name)
                            
        self.check_dependencies()
            
        self.run_preremove()
            
        for fileinfo in ctx.installdb.files(self.package_name).list:
            self.remove_file(fileinfo)
    
        self.remove_db()
        self.remove_pisi_files()

    def check_dependencies(self):
        #we only have to check the dependencies to ensure the
        #system will be consistent after this removal
        pass
        # is there any package who depends on this package?

    def remove_file(fileinfo):
        fpath = pisi.util.join_path(ctx.config.dest_dir(), fileinfo.path)
        # TODO: We have to store configuration files for futher
        # usage. Currently we'are doing it like rpm does, saving
        # with a prefix and leaving the user to edit it. In the future
        # we'll have a plan for these configuration files.
        if fileinfo.type == ctx.const.conf:
            if os.path.isfile(fpath):
                os.rename(fpath, fpath + ".pisi")
        else:
            # check if file is removed manually.
            # And we don't remove directories!
            # TODO: remove directory if there is nothing under it?
            if os.path.isfile(fpath) or os.path.islink(fpath):
                os.unlink(fpath)
            else:
                ctx.ui.warning(_('Not removing non-file, non-link %s') % fpath)

    remove_file = staticmethod(remove_file)
    
    def run_preremove(self):
        if ctx.comar:
            import pisi.comariface as comariface
            comariface.run_preremove(self.package_name)
        else:
            # TODO: store this somewhere
            pass

    def remove_pisi_files(self):
        util.clean_dir(self.package.pkg_dir())
    
    def remove_db(self):
        ctx.installdb.remove(self.package_name)
        #FIXME: this looks like a mistake!
        packagedb.remove_package(self.package_name)


def remove_single(package_name):
    Remove(package_name).run()
