# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

"""Atomic package operations such as install/remove/upgrade"""

# Standard Python Modules
import os
import shutil
import zipfile

# INARY modules
import inary
import inary.configfile
import inary.context as ctx
import inary.data
from inary.errors import PostOpsError, NotfoundError, Error, FileError
import inary.data
import inary.db
import inary.file
import inary.package
import inary.operations
import inary.uri
import inary.ui
import inary.util as util
import inary.version
import inary.trigger

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


# single package operations

class AtomicOperation(object):

    def __init__(self, ignore_dep=None):
        # self.package = package
        if ignore_dep is None:
            self.ignore_dep = ctx.config.get_option('ignore_dependency')
        else:
            self.ignore_dep = ignore_dep

        self.historydb = inary.db.historydb.HistoryDB()

    def run(self, package):
        """perform an atomic package operation"""
        pass


# possible paths of install operation
(INSTALL, REINSTALL, UPGRADE, DOWNGRADE, REMOVE) = list(range(5))
opttostr = {
    INSTALL: "install",
    REMOVE: "remove",
    REINSTALL: "reinstall",
    UPGRADE: "upgrade",
    DOWNGRADE: "downgrade"}


class Install(AtomicOperation):
    """Install class, provides install routines for inary packages"""

    @staticmethod
    def from_name(name, ignore_dep=None):
        packagedb = inary.db.packagedb.PackageDB()
        installdb = inary.db.installdb.InstallDB()
        # download package and return an installer object
        # find package in repository
        repo = packagedb.which_repo(name)
        if repo:
            repodb = inary.db.repodb.RepoDB()
            ctx.ui.debug(
                _("Package \"{0}\" found in repository \"{1}\"").format(
                    name, repo))

            repo = repodb.get_repo(repo)
            pkg = packagedb.get_package(name)
            delta = None

            # Package is installed. This is an upgrade. Check delta.
            if installdb.has_package(pkg.name):
                release = installdb.get_release(pkg.name)
                (distro, distro_release) = installdb.get_distro_release(pkg.name)
                # inary distro upgrade should not use delta support
                if distro == pkg.distribution and distro_release == pkg.distributionRelease:
                    delta = pkg.get_delta(release)

            ignore_delta = ctx.config.values.general.ignore_delta

            # If delta exists than use the delta uri.
            if delta and not ignore_delta:
                pkg_uri = delta.packageURI
                pkg_hash = delta.packageHash
            else:
                pkg_uri = pkg.packageURI
                pkg_hash = pkg.packageHash

            uri = inary.uri.URI(pkg_uri)
            if uri.is_absolute_path():
                pkg_path = str(pkg_uri)
            else:
                pkg_path = os.path.join(os.path.dirname(repo.indexuri.get_uri()),
                                        str(uri.path()))

            ctx.ui.info(
                _("Package URI: \"{}\"").format(pkg_path),
                verbose=True)

            # Bug 4113
            cached_file = inary.package.Package.is_cached(pkg_path)
            if cached_file and util.sha1_file(cached_file) != pkg_hash:
                os.unlink(cached_file)
                cached_file = None

            install_op = Install(pkg_path, ignore_dep)

            # Bug 4113
            if not cached_file:
                downloaded_file = install_op.package.filepath
                if util.sha1_file(downloaded_file) != pkg_hash:
                    raise Error(
                        _("Download Error: Package does not match the repository package."))

            return install_op
        else:
            raise Error(
                _("Package \"{}\" not found in any active repository.").format(name))

    def __init__(self, package_fname, ignore_dep=None,
                 ignore_file_conflicts=None):
        if not ctx.filesdb:
            ctx.filesdb = inary.db.filesdb.FilesDB()
        "initialize from a file name"
        super(Install, self).__init__(ignore_dep)
        if not ignore_file_conflicts:
            ignore_file_conflicts = ctx.config.get_option(
                'ignore_file_conflicts')
        self.ignore_file_conflicts = ignore_file_conflicts
        self.package_fname = package_fname
        try:
            self.package = inary.package.Package(package_fname)
            self.package.read()
        except zipfile.BadZipfile:
            raise zipfile.BadZipfile(self.package_fname)
        self.metadata = self.package.metadata
        self.files = self.package.files
        self.pkginfo = self.metadata.package
        self.installedSize = self.metadata.package.installedSize
        self.installdb = inary.db.installdb.InstallDB()
        self.operation = INSTALL
        self.store_old_paths = None
        self.old_path = None
        self.trigger = inary.trigger.Trigger()

    def install(self, ask_reinstall=True):

        # Any package should remove the package it replaces before
        self.check_replaces()
        ctx.ui.status(
            _("Installing \"{0.name}\", version {0.version}, release {0.release}").format(
                self.pkginfo), push_screen=False)
        ctx.ui.notify(
            inary.ui.installing,
            package=self.pkginfo,
            files=self.files)

        ctx.ui.info(
            _("Checking package operation availability..."), verbose=True)
        self.ask_reinstall = ask_reinstall
        ctx.ui.status(_("Checking requirements"), push_screen=False)
        self.check_requirements()
        ctx.ui.status(_("Checking versioning"), push_screen=False)
        self.check_versioning(self.pkginfo.version, self.pkginfo.release)
        ctx.ui.status(_("Checking relations"), push_screen=False)
        self.check_relations()
        ctx.ui.status(_("Checking operations"), push_screen=False)
        self.check_operation()

        # postOps from inary.operations.install and inary.operations.upgrade
        ctx.ui.status(_("Unpacking package"), push_screen=False)

        self.extract_install()

        ctx.ui.status(_("Updating database"), push_screen=False)
        self.store_inary_files()
        self.update_databases()
        ctx.ui.status(_("Syncing all buffers"), push_screen=False)
        util.fs_sync()

        ctx.ui.close()
        if self.operation == UPGRADE:
            event = inary.ui.upgraded
        else:
            event = inary.ui.installed
        ctx.ui.notify(event, package=self.pkginfo, files=self.files)
        util.xterm_title_reset()

    def check_requirements(self):
        """check system requirements"""
        # Check free space
        total_size, symbol = util.human_readable_size(util.free_space())
        if util.free_space() < self.installedSize:
            raise Error(_("Is there enought free space in your disk?"))
        ctx.ui.info(_("Free space in \'destinationdirectory\': {:.2f} {} ".format(
            total_size, symbol)), verbose=True)

    def check_replaces(self):
        for replaced in self.pkginfo.replaces:
            if self.installdb.has_package(replaced.package):
                inary.operations.remove.remove_replaced_packages(
                    [replaced.package])

    @staticmethod
    def check_versioning(version, release):
        try:
            int(release)
            inary.version.make_version(version)
        except (ValueError, inary.version.InvalidVersionError):
            raise Error(
                _("{0}-{1} is not a valid INARY version format").format(version, release))

    def check_relations(self):
        # check dependencies
        # if not ctx.config.get_option('ignore_dependency'):
        #    if not self.pkginfo.installable():
        #        raise Error(_("{} package cannot be installed unless the dependencies are satisfied").format(self.pkginfo.name))

        # If it is explicitly specified that package conflicts with this package and also
        # we passed check_conflicts tests in operations.py than this means a non-conflicting
        # pkg is in "order" to be installed that has no file conflict problem with this package.
        # PS: we need this because "order" generating code does not consider
        # conflicts.
        def really_conflicts(pkg):
            if not self.pkginfo.conflicts:
                return True

            return pkg not in [x.package for x in self.pkginfo.conflicts]

        # check file conflicts
        file_conflicts = []
        for f in self.files.list:
            pkg, existing_file = ctx.filesdb.get_file(f.path)
            if pkg:
                dst = util.join_path(ctx.config.dest_dir(), f.path)
                if pkg != self.pkginfo.name and not os.path.isdir(
                        dst) and really_conflicts(pkg):
                    file_conflicts.append((pkg, existing_file))
        if file_conflicts:
            file_conflicts_str = ""
            for (pkg, existing_file) in file_conflicts:
                file_conflicts_str += _(
                    "\"/{0}\" from \"{1}\" package\n").format(existing_file, pkg)
            msg = _('File conflicts:\n\"{}\"').format(file_conflicts_str)
            if self.ignore_file_conflicts:
                ctx.ui.warning(msg)
            else:
                raise Error(msg)

    def check_operation(self):

        self.old_pkginfo = None
        pkg = self.pkginfo

        if self.installdb.has_package(pkg.name):  # is this a reinstallation?
            (iversion_s, irelease_s) = self.installdb.get_version(pkg.name)[:2]

            # determine if same version
            if pkg.release == irelease_s:
                if self.ask_reinstall:
                    if not ctx.ui.confirm(
                            _('Re-install same version package?')):
                        raise Error(_('Package re-install declined'))
                self.operation = REINSTALL
                ctx.ui.info(_('Re-installing package.'))
            else:
                pkg_version = inary.version.make_version(pkg.version)
                iversion = inary.version.make_version(iversion_s)
                if ctx.config.get_option(
                        'store_lib_info') and pkg_version > iversion:
                    self.store_old_paths = os.path.join(
                        ctx.config.old_paths_cache_dir(), pkg.name)
                    ctx.ui.info(_('Storing old paths info.'))
                    open(
                        self.store_old_paths, "w").write(
                        "Version: {}\n".format(iversion_s))

                pkg_release = int(pkg.release)
                irelease = int(irelease_s)

                # is this an upgrade?
                # determine and report the kind of upgrade: version, release
                if pkg_release > irelease:
                    ctx.ui.info(_('Upgrading to new release.'))
                    self.operation = UPGRADE

                # is this a downgrade? confirm this action.
                if not self.operation == UPGRADE:
                    if pkg_release < irelease:
                        x = _('Downgrade to old distribution release?')
                    else:
                        x = None
                    if self.ask_reinstall and x and not ctx.ui.confirm(x):
                        raise Error(_('Package downgrade declined'))
                    self.operation = DOWNGRADE

            # schedule for reinstall

            self.old_files = self.installdb.get_files(pkg.name)
            self.old_pkginfo = self.installdb.get_info(pkg.name)
            self.old_path = self.installdb.pkg_dir(
                pkg.name, iversion_s, irelease_s)

    def preinstall(self):
        if 'postOps' in self.metadata.package.isA:
            if ctx.config.get_option(
                    'ignore_configure') or ctx.config.get_option('destdir'):
                self.installdb.mark_pending(self.pkginfo.name)
                return 0
            ctx.ui.info(_('Pre-install configuration have been run for \"{}\"'.format(
                self.pkginfo.name)), color='brightyellow')
            if not self.trigger.preinstall(self.package.pkg_dir()):
                util.clean_dir(self.package.pkg_dir())
                ctx.ui.error(
                    _('Pre-install configuration of \"{}\" package failed.').format(self.pkginfo.name))

    def postinstall(self):

        # Chowning for additional files
        # for _file in self.package.get_files().list:
        #    fpath = util.join_path(ctx.config.dest_dir(), _file.path)
        #    if os.path.islink(fpath):
        #        ctx.ui.info(_("Added symlink '{}' ").format(fpath), verbose=True)
        #    else:
        #        ctx.ui.info(_("Chowning in postinstall {0} ({1}:{2})").format(_file.path, _file.uid, _file.gid), verbose=True)
        #        os.chown(fpath, int(_file.uid), int(_file.gid))

        if 'postOps' in self.metadata.package.isA:
            if ctx.config.get_option(
                    'ignore_configure') or ctx.config.get_option('destdir'):
                self.installdb.mark_pending(self.pkginfo.name)
                return 0
            ctx.ui.info(
                _('Configuring post-install \"{}\"'.format(self.pkginfo.name)), color='brightyellow')
            if not self.trigger.postinstall(self.package.pkg_dir()):
                ctx.ui.error(
                    _('Post-install configuration of \"{}\" package failed.').format(self.pkginfo.name))
                self.installdb.mark_pending(self.pkginfo.name)
                return 0

    def extract_install(self):
        """unzip package in place"""

        ctx.ui.notify(
            inary.ui.extracting,
            package=self.pkginfo,
            files=self.files)

        def check_config_changed(config):
            fpath = util.join_path(ctx.config.dest_dir(), config.path)
            if util.config_changed(config):
                self.historydb.save_config(self.pkginfo.name, fpath)

        # Package file's path may not be relocated or content may not be changed but
        # permission may be changed
        def update_permissions():
            permissions = inary.operations.delta.find_permission_changes(
                self.old_files, self.files)
            for path, mode in permissions:
                os.chmod(path, mode)

        # Delta package does not contain the files that have the same hash as in
        # the old package's. Because it means the file has not changed. But some
        # of these files may be relocated to some other directory in the new package.
        # We handle these cases here.
        def relocate_files():
            missing_old_files = set()

            for old_file, new_file in inary.operations.delta.find_relocations(
                    self.old_files, self.files):
                old_path = os.path.join(ctx.config.dest_dir(), old_file.path)
                new_path = os.path.join(ctx.config.dest_dir(), new_file.path)

                if not os.path.lexists(old_path):
                    missing_old_files.add(old_path)
                    continue

                if os.path.lexists(new_path):
                    # If one of the parent directories is a symlink, it is possible
                    # that the new and old file paths refer to the same file.
                    # In this case, there is nothing to do here.
                    #
                    # e.g. /lib/libdl.so and /lib64/libdl.so when /lib64 is
                    # a symlink to /lib.
                    if os.path.basename(old_path) == os.path.basename(new_path) \
                            and os.path.samestat(os.lstat(old_path), os.lstat(new_path)):
                        continue

                    os.unlink(new_path)

                destdir = os.path.dirname(new_path)
                if not os.path.exists(destdir):
                    os.makedirs(destdir)

                if os.path.islink(old_path):
                    os.symlink(os.readlink(old_path), new_path)
                else:
                    shutil.copy(old_path, new_path)

            if missing_old_files:
                ctx.ui.warning(
                    _("Unable to relocate following files. Reinstallation of this package is strongly recommended."))
                for f in sorted(missing_old_files):
                    ctx.ui.warning("    - {}".format(f))

        # remove left over files from the old package.
        def clean_leftovers():
            stat_cache = {}

            files_by_name = {}
            new_paths = []
            for f in self.files.list:
                files_by_name.setdefault(
                    os.path.basename(
                        f.path), []).append(f)
                new_paths.append(f.path)

            for old_file in self.old_files.list:
                if old_file.path in new_paths:
                    continue

                old_file_path = os.path.join(
                    ctx.config.dest_dir(), old_file.path)

                try:
                    old_file_stat = os.lstat(old_file_path)
                except OSError:
                    continue

                old_filename = os.path.basename(old_file.path)

                # If one of the parent directories is a symlink, it is possible
                # that the new and old file paths refer to the same file.
                # In this case, we must not remove the old file.
                #
                # e.g. /lib/libdl.so and /lib64/libdl.so when /lib64 is
                # a symlink to /lib.
                for new_file in files_by_name.get(old_filename, []):

                    new_file_stat = stat_cache.get(new_file.path)

                    if new_file_stat is None:
                        path = os.path.join(
                            ctx.config.dest_dir(), new_file.path)
                        try:
                            new_file_stat = os.lstat(path)
                        except OSError:
                            continue

                        stat_cache[new_file.path] = new_file_stat

                    if os.path.samestat(new_file_stat, old_file_stat):
                        break

                else:

                    remove_permanent = not ctx.config.get_option(
                        "preserve_permanent")

                    Remove.remove_file(
                        old_file,
                        self.pkginfo.name,
                        remove_permanent,
                        store_old_paths=self.store_old_paths)

        if self.operation == REINSTALL:
            # get 'config' typed file objects replace is not set
            # new = [x for x in self.files.list if x.type == 'config' and not
            # x.replace, self.files.list]
            new = [x for x in self.files.list if x.type == 'config']
            old = [x for x in self.old_files.list if x.type == 'config']

            # get config path lists
            newconfig = set(str(x.path) for x in new)
            oldconfig = set(str(x.path) for x in old)

            config_overlaps = newconfig & oldconfig
            if config_overlaps:
                files = [x for x in old if x.path in config_overlaps]
                for f in files:
                    check_config_changed(f)
        else:
            for f in self.files.list:
                if f.type == 'config':
                    # there may be left over config files
                    check_config_changed(f)

        if self.package_fname.endswith(ctx.const.delta_package_suffix):
            relocate_files()
            update_permissions()

        self.package.extract_install(ctx.config.dest_dir())
        if self.operation == REINSTALL or self.operation == UPGRADE:
            clean_leftovers()

    def store_postops(self):
        """stores postops script temporarly"""
        ctx.ui.info(_("Precaching postoperations.py file"), verbose=True)

        if 'postOps' in self.metadata.package.isA:
            for postops in ctx.const.postops:
                try:
                    self.package.extract_file_synced(
                        postops, ctx.config.tmp_dir())
                except:
                    pass

    def store_inary_files(self):
        """put files.xml, metadata.xml, somewhere in the file system. We'll need these in future..."""
        ctx.ui.info(
            _("Storing inary files (files.xml, metadata.xml and whether postoperations.py)"), verbose=True)
        self.package.extract_file_synced(
            ctx.const.files_xml, self.package.pkg_dir())
        self.package.extract_file_synced(
            ctx.const.metadata_xml, self.package.pkg_dir())
        if 'postOps' in self.metadata.package.isA:
            for postops in ctx.const.postops:
                try:
                    self.package.extract_file_synced(
                        postops, self.package.pkg_dir())
                except:
                    pass

    def update_databases(self):
        """update databases"""

        if self.installdb.has_package(self.pkginfo.name):
            if self.operation == (UPGRADE or DOWNGRADE or REINSTALL):
                self.installdb.remove_package(self.pkginfo)
                self.installdb.add_package(self.pkginfo)

            release = self.installdb.get_release(self.pkginfo.name)
            actions = self.pkginfo.get_update_actions(release)
        else:
            actions = self.pkginfo.get_update_actions("1")

        for package_name in actions.get("serviceRestart", []):
            self.installdb.mark_needs_restart(package_name)

        for package_name in actions.get("systemRestart", []):
            self.installdb.mark_needs_reboot(package_name)

        # filesdb
        ctx.ui.info(
            _('Adding files of \"{}\" package to database...').format(
                self.metadata.package.name),
            color='faintpurple')
        ctx.filesdb.add_files(self.metadata.package.name, self.files)

        # installed packages
        self.installdb.add_package(self.pkginfo)

        otype = "delta" if self.package_fname.endswith(
            ctx.const.delta_package_suffix) else None
        self.historydb.add_and_update(pkgBefore=self.old_pkginfo, pkgAfter=self.pkginfo,
                                      operation=opttostr[self.operation], otype=otype)

        if self.operation == (UPGRADE or DOWNGRADE or REINSTALL):
            util.clean_dir(self.old_path)


def install_single(pkg, upgrade=False):
    """install a single package from URI or ID"""
    url = inary.uri.URI(pkg)
    # Check if we are dealing with a remote file or a real path of
    # package filename. Otherwise we'll try installing a package from
    # the package repository.
    if url.is_remote_file() or os.path.exists(url.uri):
        install_single_file(pkg, upgrade)
    else:
        install_single_name(pkg, upgrade)


def install_single_file(pkg_location, upgrade=False):
    """install a package file"""
    ctx.ui.info(_('Installing => [{}]'.format(pkg_location)), color='yellow')
    install = Install(pkg_location)
    __install(install, upgrade)


def install_single_name(name, upgrade=False):
    """install a single package from ID"""
    install = Install.from_name(name)
    __install(install, upgrade)


def __install(install, upgrade=False):
    '''Standard installation function'''
    install.store_postops()
    install.preinstall()
    install.install(not upgrade)
    install.postinstall()


class Remove(AtomicOperation):

    def __init__(self, package_name, ignore_dep=None, store_old_paths=None):
        if not ctx.filesdb:
            ctx.filesdb = inary.db.filesdb.FilesDB()
        super(Remove, self).__init__(ignore_dep)
        self.installdb = inary.db.installdb.InstallDB()
        self.package_name = package_name
        self.package = self.installdb.get_package(self.package_name)
        self.metadata = self.installdb.get_metadata(self.package_name)
        self.store_old_paths = store_old_paths
        self.trigger = inary.trigger.Trigger()
        try:
            self.files = self.installdb.get_files(self.package_name)
        except Error as e:
            # for some reason file was deleted, we still allow removes!
            ctx.ui.error(str(e))
            ctx.ui.warning(
                _('File list could not be read for \"{}\" package, continuing removal.').format(package_name))
            self.files = inary.data.files.Files()

    def run(self):
        """Remove a single package"""
        ctx.ui.notify(
            inary.ui.removing,
            package=self.package,
            files=self.files)
        ctx.ui.status(
            _("Removing \"{0.name}\", version {0.version}, release {0.release}").format(
                self.package), push_screen=False)

        if not self.installdb.has_package(self.package_name):
            raise Exception(_('Trying to remove nonexistent package ')
                            + self.package_name)

        self.check_dependencies()
        if not ctx.config.get_option(
                'ignore_configure') or ctx.config.get_option('destdir'):
            self.run_preremove()
        for fileinfo in self.files.list:
            self.remove_file(fileinfo, self.package_name, True)

        if not ctx.config.get_option(
                'ignore_configure') or ctx.config.get_option('destdir'):
            self.run_postremove()

        self.update_databases()

        self.remove_inary_files()
        ctx.ui.close()
        ctx.ui.notify(inary.ui.removed, package=self.package, files=self.files)
        util.xterm_title_reset()

    def check_dependencies(self):
        # FIXME: why is this not implemented? -- exa
        # we only have to check the dependencies to ensure the
        # system will be consistent after this removal
        pass
        # is there any package who depends on this package?

    @staticmethod
    def remove_file(fileinfo, package_name,
                    remove_permanent=False, store_old_paths=None):

        if fileinfo.permanent and not remove_permanent:
            return

        fpath = util.join_path(ctx.config.dest_dir(), fileinfo.path)

        historydb = inary.db.historydb.HistoryDB()
        # we should check if the file belongs to another
        # package (this can legitimately occur while upgrading
        # two packages such that a file has moved from one package to
        # another as in #2911)
        pkg = ctx.filesdb.get_filename(fileinfo.path)
        if pkg and pkg != package_name:
            ctx.ui.warning(
                _('Not removing conflicted file : \"{}\"').format(fpath))
            return

        if fileinfo.type == ctx.const.conf:
            # config files are precious, leave them as they are
            # unless they are the same as provided by package.
            # remove symlinks as they are, cause if the hash of the
            # file it links has changed, it will be kept as is,
            # and when the package is reinstalled the symlink will
            # link to that changed file again.
            try:
                if os.path.islink(fpath) or util.sha1_file(
                        fpath) == fileinfo.hash:
                    os.unlink(fpath)
                else:
                    # keep changed file in history
                    historydb.save_config(package_name, fpath)

                    # after saving to history db, remove the config file any
                    # way
                    if ctx.config.get_option("purge"):
                        os.unlink(fpath)
            except FileError:
                pass
        else:
            if os.path.isfile(fpath) or os.path.islink(fpath):
                os.unlink(fpath)
                if store_old_paths:
                    open(store_old_paths, "a").write("{}\n".format(fpath))
            elif os.path.isdir(fpath) and not os.listdir(fpath):
                os.rmdir(fpath)
            else:
                ctx.ui.warning(
                    _('Installed file \"{}\" does not exist on system [Probably you manually deleted]').format(fpath))
                return

        # remove emptied directories
        dpath = os.path.dirname(fpath)
        while dpath != '/' and os.path.exists(dpath) and not os.listdir(dpath):
            os.rmdir(dpath)
            dpath = os.path.dirname(dpath)

    def run_preremove(self):
        if 'postOps' in self.metadata.package.isA:
            ctx.ui.info(_('Pre-remove configuration have been run for \"{}\"'.format(
                self.package_name)), color='brightyellow')
            self.trigger.preremove(self.package.pkg_dir())

    def run_postremove(self):
        if 'postOps' in self.metadata.package.isA:
            ctx.ui.info(_('Post-remove configuration have been run for  \"{}\"'.format(
                self.package_name)), color='brightyellow')
            self.trigger.postremove(self.package.pkg_dir())

    def update_databases(self):
        self.remove_db()
        self.historydb.add_and_update(
            pkgBefore=self.package, operation="remove")

    def remove_inary_files(self):
        ctx.ui.info(
            _('Removing files of \"{}\" package from system...').format(
                self.package_name),
            color='faintpurple')
        util.clean_dir(self.package.pkg_dir())

    def remove_db(self):
        ctx.ui.info(
            _('Removing files of \"{}\" package from database...').format(
                self.package_name),
            color='faintyellow')
        self.installdb.remove_package(self.package_name)
        ctx.filesdb.remove_files(self.files.list)


# FIX:DB
#         # FIXME: something goes wrong here, if we use ctx operations ends up with segmentation fault!
#         inary.db.packagedb.remove_tracking_package(self.package_name)


def remove_single(package_name):
    Remove(package_name).run()
