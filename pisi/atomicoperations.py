# -*- coding: utf-8 -*-
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
# Author:  Eray Ozkural <eray@uludag.org.tr>

"Atomic package operations such as install/remove/upgrade"

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import sys
import os
import bsddb3.db as db

import pisi
import pisi.context as ctx
import pisi.packagedb as packagedb
import pisi.dependency as dependency
import pisi.util as util
from pisi.specfile import *
from pisi.package import Package
from pisi.metadata import MetaData
from pisi.files import Files
from pisi.uri import URI
import pisi.ui
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

    @staticmethod
    def from_name(name):
        # download package and return an installer object
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
    
            return Install(pkg_path)
        else:
            raise Error(_("Package %s not found in any active repository.") % name)

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
        ctx.ui.status(_('Installing %s, version %s, release %s, build %s') %
                (self.pkginfo.name, self.pkginfo.version,
                 self.pkginfo.release, self.pkginfo.build))
        ctx.ui.notify(pisi.ui.installing, package = self.pkginfo, files = self.files)

        self.ask_reinstall = ask_reinstall
        self.check_requirements()
        self.check_relations()
        self.check_reinstall()
        self.extract_install()
        self.store_pisi_files()

        self.config_later = False

        if self.metadata.package.providesComar:
            if ctx.comar:
                import pisi.comariface as comariface
                self.register_comar_scripts()
            else:
                self.config_later = True # configure-pending will register scripts later

        if 'System.Package' in [x.om for x in self.metadata.package.providesComar]:
            if ctx.comar:
                ctx.ui.notify(pisi.ui.configuring, package = self.pkginfo, files = self.files)
                comariface.run_postinstall(self.pkginfo.name)
                ctx.ui.notify(pisi.ui.configured, package = self.pkginfo, files = self.files)
            else:
                self.config_later = True

        txn = ctx.dbenv.txn_begin()
        try:
            self.update_databases(txn)
            txn.commit()
        except db.DBError, e:
            txn.abort()
            raise e

        self.update_environment()
        ctx.ui.status()
        if self.upgrade:
            event = pisi.ui.upgraded
        else:
            event = pisi.ui.installed
        ctx.ui.notify(event, package = self.pkginfo, files = self.files)

    def check_requirements(self):
        """check system requirements"""
        #TODO: IS THERE ENOUGH SPACE?
        # what to do if / is split into /usr, /var, etc.
        # check comar
        if self.metadata.package.providesComar and ctx.comar:
            import pisi.comariface as comariface
            com = comariface.make_com()

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
        self.upgrade = False
        if ctx.installdb.is_installed(pkg.name): # is this a reinstallation?
            (iversion, irelease, ibuild) = ctx.installdb.get_version(pkg.name)

            # determine if same version
            self.same_ver = False
            ignore_build = ctx.config.options and ctx.config.options.ignore_build_no
            if (not ibuild) or (not pkg.build) or ignore_build:
                # we don't look at builds to compare two package versions
                if pkg.release == irelease:
                    self.same_ver = True
            else:
                if pkg.build == ibuild:
                    self.same_ver = True

            if self.same_ver:
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
                self.upgrade = upgrade

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
            self.old_path = ctx.installdb.pkg_dir(pkg.name, iversion, irelease)
            self.reinstall = True
            Remove(pkg.name).run_preremove()

    def extract_install(self):
        "unzip package in place"

        ctx.ui.notify(pisi.ui.extracting, package = self.pkginfo, files = self.files)
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

    def update_databases(self, txn):
        "update databases"
        if self.reinstall:
            Remove(self.metadata.package.name).remove_db(txn)
            if not self.same_ver:
                Remove.remove_pisi_files(self.old_path)

        # installdb
        ctx.installdb.install(self.metadata.package.name,
                          self.metadata.package.version,
                          self.metadata.package.release,
                          self.metadata.package.build,
                          self.metadata.package.distribution,
                          self.config_later, 
                          False,
                          txn)

        # filesdb
        ctx.filesdb.add_files(self.metadata.package.name, self.files, txn)

        # installed packages
        packagedb.inst_packagedb.add_package(self.pkginfo, txn)

    def update_environment(self):
        # check if we have any shared objects or anything under
        # /etc/env.d
        shared = False
        for x in self.files.list:
            if x.path.endswith('.so') or x.path.startswith('/etc/env.d'):
                shared = True
                break
        if not ctx.get_option('bypass_ldconfig'):
            if shared:
                ctx.ui.info(_("Regenerating /etc/ld.so.cache..."))
                util.env_update()
        else:
            ctx.ui.warning(_("Bypassing ldconfig"))

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
    install = Install.from_name(name)
    install.install(not upgrade)

class Remove(AtomicOperation):
    
    def __init__(self, package_name, ignore_dep = None):
        super(Remove, self).__init__(ignore_dep)
        self.package_name = package_name
        self.package = packagedb.get_package(self.package_name)
        try:
            self.files = ctx.installdb.files(self.package_name)
        except pisi.Error, e:
            # for some reason file was deleted, we still allow removes!
            ctx.ui.error(unicode(e))
            ctx.ui.warning(_('File list could not be read for package %s, continuing removal.') % package_name)
            self.files = Files()

    def run(self):
        """Remove a single package"""
        inst_packagedb = packagedb.inst_packagedb
       
        ctx.ui.status(_('Removing package %s') % self.package_name)
        ctx.ui.notify(pisi.ui.removing, package = self.package, files = self.files)
        if not ctx.installdb.is_installed(self.package_name):
            raise Exception(_('Trying to remove nonexistent package ')
                            + self.package_name)
                            
        self.check_dependencies()
            
        self.run_preremove()
            
        for fileinfo in self.files.list:
            self.remove_file(fileinfo)

        txn = ctx.dbenv.txn_begin()
        try:
            self.remove_db(txn)
            txn.commit()
        except db.DBError, e:
            txn.abort()
            raise e

        self.remove_pisi_files(self.package.pkg_dir())
        ctx.ui.status()
        ctx.ui.notify(pisi.ui.removed, package = self.package, files = self.files)

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
        if fileinfo.permanent:
            # do not remove precious files :)
            # just write anything permanent="true" for instance
            return
        if fileinfo.type == "config":
            if os.path.isfile(fpath):
                os.rename(fpath, fpath + ".oldconfig")
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
        if ctx.comar and self.package.providesComar:
            import pisi.comariface as comariface
            comariface.run_preremove(self.package_name)
        else:
            # TODO: store this somewhere
            pass

    @staticmethod
    def remove_pisi_files(path):
        #TODO: what does this have to do with pisi files??
        util.clean_dir(path)
    
    def remove_db(self, txn):
        ctx.installdb.remove(self.package_name, txn)
        ctx.filesdb.remove_files(self.files, txn)
        if packagedb.thirdparty_packagedb.has_package(self.package_name, txn):
            packagedb.thirdparty_packagedb.remove_package(self.package_name, txn)
        if packagedb.inst_packagedb.has_package(self.package_name, txn):
            packagedb.inst_packagedb.remove_package(self.package_name, txn)


def remove_single(package_name):
    Remove(package_name).run()

def __is_virtual_upgrade(metadata):

    pkg = metadata.package

    (iversion, irelease, ibuild) = ctx.installdb.get_version(pkg.name)
    
    upgrade = False
    if pkg.version > iversion:
        upgrade = True
    elif pkg.release > irelease:
        upgrade = True
    elif (ibuild and pkg.build and pkg.build > ibuild):
        upgrade = True  
    
    return upgrade

def virtual_install(metadata, files, txn):
    """Recreate the package info for rebuilddb command"""
    pkg = metadata.package

    # normally this can't be true. Just for backward compatibility
    # TODO: for speed only ctx.installdb.install exception can be
    # handled but this is much cleaner
    if ctx.installdb.is_installed(pkg.name, txn):
        if __is_virtual_upgrade(metadata):
            ctx.installdb.remove(pkg.name, txn)
            packagedb.remove_package(pkg.name, txn)
            ctx.filesdb.remove_files(ctx.installdb.files(pkg.name), txn)
        else:
            return

    pkginfo = metadata.package
    
    # installdb
    ctx.installdb.install(metadata.package.name,
                          metadata.package.version,
                          metadata.package.release,
                          metadata.package.build,
                          metadata.package.distribution,
                          False,
                          True,
                          txn)

    # filesdb
    ctx.filesdb.add_files(metadata.package.name, files, txn)
    
    # installed packages
    packagedb.inst_packagedb.add_package(pkginfo, txn)

def resurrect_package(package_fn):
    """Resurrect the package in the PiSi databases"""

    from os.path import exists

    metadata_xml = util.join_path(ctx.config.lib_dir(), 'package', 
                                  package_fn, ctx.const.metadata_xml)
    if not exists(metadata_xml):
       raise Error, _("Metadata XML '%s' cannot be found") % metadata_xml

    metadata = MetaData()
    metadata.read(metadata_xml)

    errs = metadata.errors()
    if errs:   
       util.Checks.print_errors(errs)
       raise Error, _("MetaData format wrong (%s)") % package_fn

    # FIXME: there won't be any previous versions of the same package under /var/lib/pisi
    # therefore there won't be any need for this check and __is_virtual_upgrade function
    # this is just for backward compatibility for sometime

    # yes, this is an ugly hack
    passed = False
    if ctx.installdb.is_installed(metadata.package.name):
        passed = True
    
    if not passed:
        ctx.ui.info(_('* Adding \'%s\' to db... ') % (metadata.package.name), noln=True)
    
    files_xml = util.join_path(ctx.config.lib_dir(), 'package',
                               package_fn, ctx.const.files_xml)
    if not exists(files_xml):
       raise Error, _("Files XML '%s' cannot be found") % files_xml

    files = Files()
    files.read(files_xml)

    if files.errors():
       raise Error, _("Invalid %s") % ctx.const.files_xml

    import pisi.atomicoperations
    def f(txn):
        pisi.atomicoperations.virtual_install(metadata, files, txn)
    ctx.txn_proc(f)
    if not passed:
        ctx.ui.info(_('OK.'))
