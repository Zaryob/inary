# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

"""Atomic package operations such as install/remove/upgrade"""

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import os
import shutil
import zipfile

import inary
import inary.context as ctx
import inary.data
import inary.errors
import inary.db
import inary.operations
import inary.uri
import inary.ui
import inary.util as util
import inary.version
import inary.data.pgraph as pgraph

class Error(inary.Error):
    pass

class NotfoundError(inary.Error):
    pass

# single package operations

class AtomicOperation(object):

    def __init__(self, ignore_dep = None):
        #self.package = package
        if ignore_dep==None:
            self.ignore_dep = ctx.config.get_option('ignore_dependency')
        else:
            self.ignore_dep = ignore_dep

        self.historydb = inary.db.historydb.HistoryDB()

    def run(self, package):
        "perform an atomic package operation"
        pass

# possible paths of install operation
(INSTALL, REINSTALL, UPGRADE, DOWNGRADE, REMOVE) = list(range(5))
opttostr = {INSTALL:"install", REMOVE:"remove", REINSTALL:"reinstall", UPGRADE:"upgrade", DOWNGRADE:"downgrade"}

class Install(AtomicOperation):
    "Install class, provides install routines for inary packages"

    @staticmethod
    def from_name(name, ignore_dep = None):
        packagedb = inary.db.packagedb.PackageDB()
        # download package and return an installer object
        # find package in repository
        repo = packagedb.which_repo(name)
        if repo:
            repodb = inary.db.repodb.RepoDB()
            ctx.ui.info(_("Package {0} found in repository {1}").format(name, repo))

            repo = repodb.get_repo(repo)
            pkg = packagedb.get_package(name)
            delta = None

            installdb = inary.db.installdb.InstallDB()
            # Package is installed. This is an upgrade. Check delta.
            if installdb.has_package(pkg.name):
                (version, release, build, distro, distro_release) = installdb.get_version_and_distro_release(pkg.name)
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

            ctx.ui.info(_("Package URI: {}").format(pkg_path), verbose=True)

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
                    raise inary.Error(_("Download Error: Package does not match the repository package."))

            return install_op
        else:
            raise Error(_("Package {} not found in any active repository.").format(name))

    def __init__(self, package_fname, ignore_dep = None, ignore_file_conflicts = None):
        if not ctx.filesdb: ctx.filesdb = inary.db.filesdb.FilesDB()
        "initialize from a file name"
        super(Install, self).__init__(ignore_dep)
        if not ignore_file_conflicts:
            ignore_file_conflicts = ctx.get_option('ignore_file_conflicts')
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
        self.installdb = inary.db.installdb.InstallDB()
        self.operation = INSTALL
        self.store_old_paths = None

    def install(self, ask_reinstall = True):

        # Any package should remove the package it replaces before
        self.check_replaces()

        ctx.ui.status(_('Installing {0.name}, version {0.version}, release {0.release}').format(self.pkginfo))

        ctx.ui.notify(inary.ui.installing, package=self.pkginfo, files=self.files)

        self.ask_reinstall = ask_reinstall
        self.check_requirements()
        self.check_versioning(self.pkginfo.version, self.pkginfo.release)
        self.check_relations()
        self.check_operation()

        ctx.disable_keyboard_interrupts()

        self.extract_install()
        self.store_inary_files()
        self.postinstall()
        self.update_databases()

        ctx.enable_keyboard_interrupts()

        ctx.ui.close()
        if self.operation == UPGRADE:
            event = inary.ui.upgraded
        else:
            event = inary.ui.installed
        ctx.ui.notify(event, package = self.pkginfo, files = self.files)

    def check_requirements(self):
        """check system requirements"""
        #TODO: IS THERE ENOUGH SPACE?
        # what to do if / is split into /usr, /var, etc.
        # check scom
        if self.metadata.package.providesScom and ctx.scom:
            import inary.scomiface as scomiface
            scomiface.get_link()

    def check_replaces(self):
        for replaced in self.pkginfo.replaces:
            if self.installdb.has_package(replaced.package):
                inary.operations.remove.remove_replaced_packages([replaced.package])

    def check_versioning(self, version, release):
        try:
            int(release)
            inary.version.make_version(version)
        except (ValueError, inary.version.InvalidVersionError):
            raise Error(_("{0}-{1} is not a valid INARY version format").format(version, release))

    def check_relations(self):
        # check dependencies
        if not ctx.config.get_option('ignore_dependency'):
            if not self.pkginfo.installable():
                raise Error(_("{} package cannot be installed unless the dependencies are satisfied").format(self.pkginfo.name))

        # If it is explicitly specified that package conflicts with this package and also
        # we passed check_conflicts tests in operations.py than this means a non-conflicting
        # pkg is in "order" to be installed that has no file conflict problem with this package.
        # PS: we need this because "order" generating code does not consider conflicts.
        def really_conflicts(pkg):
            if not self.pkginfo.conflicts:
                return True

            return not pkg in [x.package for x in self.pkginfo.conflicts]

        # check file conflicts
        file_conflicts = []
        for f in self.files.list:
            pkg, existing_file = ctx.filesdb.get_file(f.path)
            if pkg:
                dst = util.join_path(ctx.config.dest_dir(), f.path)
                if pkg != self.pkginfo.name and not os.path.isdir(dst) and really_conflicts(pkg):
                    file_conflicts.append( (pkg, existing_file) )
        if file_conflicts:
            file_conflicts_str = ""
            for (pkg, existing_file) in file_conflicts:
                file_conflicts_str += _("/{0} from {1} package\n").format(existing_file, pkg)
            msg = _('File conflicts:\n{}').format(file_conflicts_str)
            if self.ignore_file_conflicts:
                ctx.ui.warning(msg)
            else:
                raise Error(msg)

    def check_operation(self):

        self.old_pkginfo = None
        pkg = self.pkginfo

        if self.installdb.has_package(pkg.name): # is this a reinstallation?
            ipkg = self.installdb.get_package(pkg.name)
            (iversion_s, irelease_s, ibuild) = self.installdb.get_version(pkg.name)

            # determine if same version
            if pkg.release == irelease_s:
                if self.ask_reinstall:
                    if not ctx.ui.confirm(_('Re-install same version package?')):
                        raise Error(_('Package re-install declined'))
                self.operation = REINSTALL
            else:
                pkg_version = inary.version.make_version(pkg.version)
                iversion = inary.version.make_version(iversion_s)
                if ctx.get_option('store_lib_info') and pkg_version > iversion:
                    self.store_old_paths = os.path.join(ctx.config.old_paths_cache_dir(), pkg.name)
                    ctx.ui.info(_('Storing old paths info'))
                    open(self.store_old_paths, "w").write("Version: {}\n".format(iversion_s))

                pkg_release = int(pkg.release)
                irelease = int(irelease_s)

                # is this an upgrade?
                # determine and report the kind of upgrade: version, release
                if pkg_version > iversion:
                    ctx.ui.info(_('Upgrading to new upstream version'))
                    self.operation = UPGRADE
                elif pkg_release > irelease:
                    ctx.ui.info(_('Upgrading to new distribution release'))
                    self.operation = UPGRADE

                # is this a downgrade? confirm this action.
                if not self.operation == UPGRADE:
                    if pkg_version < iversion:
                        #x = _('Downgrade to old upstream version?')
                        x = None
                    elif pkg_release < irelease:
                        x = _('Downgrade to old distribution release?')
                    else:
                        x = None
                    if self.ask_reinstall and x and not ctx.ui.confirm(x):
                        raise Error(_('Package downgrade declined'))
                    self.operation = DOWNGRADE

            # schedule for reinstall
            self.old_files = self.installdb.get_files(pkg.name)
            self.old_pkginfo = self.installdb.get_info(pkg.name)
            self.old_path = self.installdb.pkg_dir(pkg.name, iversion_s, irelease_s)
            self.remove_old = Remove(pkg.name, store_old_paths = self.store_old_paths)
            self.remove_old.run_preremove()
            self.remove_old.run_postremove()

    def reinstall(self):
        return not self.operation == INSTALL

    def postinstall(self):
        self.config_later = False

        # Chowning for additional files
        for _file in self.package.get_files().list:
            fpath = util.join_path(ctx.config.dest_dir(), _file.path)
            ctx.ui.debug("* Chowning in postinstall ({0}:{1})".format(_file.uid, _file.gid))
            os.chown(fpath, int(_file.uid), int(_file.gid))

        if ctx.scom:
            import inary.scomiface
            try:
                if self.operation == UPGRADE or self.operation == DOWNGRADE:
                    fromVersion = self.old_pkginfo.version
                    fromRelease = self.old_pkginfo.release
                else:
                    fromVersion = None
                    fromRelease = None
                ctx.ui.notify(inary.ui.configuring, package = self.pkginfo, files = self.files)
                inary.scomiface.post_install(
                    self.pkginfo.name,
                    self.metadata.package.providesScom,
                    self.package.scom_dir(),
                    os.path.join(self.package.pkg_dir(), ctx.const.metadata_xml),
                    os.path.join(self.package.pkg_dir(), ctx.const.files_xml),
                    fromVersion,
                    fromRelease,
                    self.metadata.package.version,
                    self.metadata.package.release
                    )
                ctx.ui.notify(inary.ui.configured, package = self.pkginfo, files = self.files)
            except inary.scomiface.Error:
                ctx.ui.warning(_('{} configuration failed.').format(self.pkginfo.name))
                self.config_later = True
        else:
            self.config_later = True

    def extract_install(self):
        "unzip package in place"

        ctx.ui.notify(inary.ui.extracting, package = self.pkginfo, files = self.files)

        config_changed = []
        def check_config_changed(config):
            fpath = util.join_path(ctx.config.dest_dir(), config.path)
            if util.config_changed(config):
                config_changed.append(fpath)
                self.historydb.save_config(self.pkginfo.name, fpath)
                if os.path.exists(fpath + '.old'):
                    os.unlink(fpath + '.old')
                os.rename(fpath, fpath + '.old')

        # old config files are kept as they are. New config files from the installed
        # packages are saved with ".newconfig" string appended to their names.
        def rename_configs():
            for path in config_changed:
                newconfig = path + '.newconfig'
                oldconfig = path + '.old'
                if os.path.exists(newconfig):
                    os.unlink(newconfig)

                # In the case of delta packages: the old package and the new package
                # may contain same config typed files with same hashes, so the delta
                # package will not have that config file. In order to protect user
                # changed config files, they are renamed with ".old" prefix in case
                # of the hashes of these files on the filesystem and the new config
                # file that is coming from the new package. But in delta package case
                # with the given scenario there wont be any, so we can pass this one.
                # If the config files were not be the same between these packages the
                # delta package would have it and extract it and the path would point
                # to that new config file. If they are same and the user had changed
                # that file and using the changed config file, there is no problem
                # here.
                if os.path.exists(path):
                    os.rename(path, newconfig)

                os.rename(oldconfig, path)

        # Package file's path may not be relocated or content may not be changed but
        # permission may be changed
        def update_permissions():
            permissions = inary.operations.delta.find_permission_changes(self.old_files, self.files)
            for path, mode in permissions:
                os.chmod(path, mode)

        # Delta package does not contain the files that have the same hash as in
        # the old package's. Because it means the file has not changed. But some
        # of these files may be relocated to some other directory in the new package.
        # We handle these cases here.
        def relocate_files():
            missing_old_files = set()

            for old_file, new_file in inary.operations.delta.find_relocations(self.old_files, self.files):
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
                ctx.ui.warning(_("Unable to relocate following files. Reinstallation of this package is strongly recommended."))
                for f in sorted(missing_old_files):
                    ctx.ui.warning("    - {}".format(f))

        # remove left over files from the old package.
        def clean_leftovers():
            stat_cache = {}

            files_by_name = {}
            new_paths = []
            for f in self.files.list:
                files_by_name.setdefault(os.path.basename(f.path), []).append(f)
                new_paths.append(f.path)

            for old_file in self.old_files.list:
                if old_file.path in new_paths:
                    continue

                old_file_path = os.path.join(ctx.config.dest_dir(), old_file.path)

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
                        path = os.path.join(ctx.config.dest_dir(), new_file.path)
                        try:
                            new_file_stat = os.lstat(path)
                        except OSError:
                            continue

                        stat_cache[new_file.path] = new_file_stat

                    if os.path.samestat(new_file_stat, old_file_stat):
                        break
                else:
                    Remove.remove_file(old_file, self.pkginfo.name, store_old_paths=self.store_old_paths)

        if self.reinstall():
            # get 'config' typed file objects replace is not set
            #new = [x for x in self.files.list if x.type == 'config' and not x.replace, self.files.list]
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

        if config_changed:
            rename_configs()

        if self.reinstall():
            clean_leftovers()


    def store_inary_files(self):
        """put files.xml, metadata.xml, scom scripts
        somewhere in the file system. We'll need these in future..."""

        if self.reinstall():
            util.clean_dir(self.old_path)

        self.package.extract_file_synced(ctx.const.files_xml, self.package.pkg_dir())
        self.package.extract_file_synced(ctx.const.metadata_xml, self.package.pkg_dir())

        for pscom in self.metadata.package.providesScom:
            fpath = os.path.join(ctx.const.scom_dir, pscom.script)
            # comar prefix is added to the pkg_dir while extracting comar
            # script file. so we'll use pkg_dir as destination.
            ctx.ui.info(_('Storing {}').format(fpath), verbose=True)
            self.package.extract_file_synced(fpath, self.package.pkg_dir())

    def update_databases(self):
        "update databases"
        if self.reinstall():
            self.remove_old.remove_db()

        if self.config_later:
            self.installdb.mark_pending(self.pkginfo.name)

        # need service or system restart?
        if self.installdb.has_package(self.pkginfo.name):
            (version, release, build) = self.installdb.get_version(self.pkginfo.name)
            actions = self.pkginfo.get_update_actions(release)
        else:
            actions = self.pkginfo.get_update_actions("1")

        for package_name in actions.get("serviceRestart", []):
            inary.db.installdb.InstallDB().mark_needs_restart(package)

        for package_name in actions.get("systemRestart", []):
            inary.db.installdb.InstallDB().mark_needs_reboot(package)

        # filesdb
        ctx.filesdb.add_files(self.metadata.package.name, self.files)

        # installed packages
        self.installdb.add_package(self.pkginfo)

        otype = "delta" if self.package_fname.endswith(ctx.const.delta_package_suffix) else None
        self.historydb.add_and_update(pkgBefore=self.old_pkginfo, pkgAfter=self.pkginfo, operation=opttostr[self.operation], otype=otype)

def install_single(pkg, upgrade = False):
    """install a single package from URI or ID"""
    url = inary.uri.URI(pkg)
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

    def __init__(self, package_name, ignore_dep = None, store_old_paths = None):
        if not ctx.filesdb: ctx.filesdb = inary.db.filesdb.FilesDB()
        super(Remove, self).__init__(ignore_dep)
        self.installdb = inary.db.installdb.InstallDB()
        self.package_name = package_name
        self.package = self.installdb.get_package(self.package_name)
        self.store_old_paths = store_old_paths
        try:
            self.files = self.installdb.get_files(self.package_name)
        except inary.Error as e:
            # for some reason file was deleted, we still allow removes!
            ctx.ui.error(str(e))
            ctx.ui.warning(_('File list could not be read for package {}, continuing removal.').format(package_name))
            self.files = inary.files.Files()

    def run(self):
        """Remove a single package"""

        ctx.ui.status(_('Removing package {}').format(self.package_name))
        ctx.ui.notify(inary.ui.removing, package = self.package, files = self.files)
        if not self.installdb.has_package(self.package_name):
            raise Exception(_('Trying to remove nonexistent package ')
                            + self.package_name)

        self.check_dependencies()

        self.run_preremove()
        for fileinfo in self.files.list:
            self.remove_file(fileinfo, self.package_name, True)

        self.run_postremove()

        self.update_databases()

        self.remove_inary_files()
        ctx.ui.close()
        ctx.ui.notify(inary.ui.removed, package = self.package, files = self.files)

    def check_dependencies(self):
        #FIXME: why is this not implemented? -- exa
        #we only have to check the dependencies to ensure the
        #system will be consistent after this removal
        pass
        # is there any package who depends on this package?

    @staticmethod
    def remove_file(fileinfo, package_name, remove_permanent=False, store_old_paths=None):

        if fileinfo.permanent and not remove_permanent:
            return

        fpath = util.join_path(ctx.config.dest_dir(), fileinfo.path)

        historydb = inary.db.historydb.HistoryDB()
        # we should check if the file belongs to another
        # package (this can legitimately occur while upgrading
        # two packages such that a file has moved from one package to
        # another as in #2911)
        pkg, existing_file = ctx.filesdb.get_file(fileinfo.path)
        if pkg != package_name:
            ctx.ui.warning(_('Not removing conflicted file : {}').format(fpath))
            return

        if fileinfo.type == ctx.const.conf:
            # config files are precious, leave them as they are
            # unless they are the same as provided by package.
            # remove symlinks as they are, cause if the hash of the
            # file it links has changed, it will be kept as is,
            # and when the package is reinstalled the symlink will
            # link to that changed file again.
            try:
                if os.path.islink(fpath) or util.sha1_file(fpath) == fileinfo.hash:
                    os.unlink(fpath)
                else:
                    # keep changed file in history
                    historydb.save_config(package_name, fpath)

                    # after saving to history db, remove the config file any way
                    if ctx.get_option("purge"):
                        os.unlink(fpath)
            except util.FileError:
                pass
        else:
            if os.path.isfile(fpath) or os.path.islink(fpath):
                os.unlink(fpath)
                if store_old_paths:
                    open(store_old_paths, "a").write("{}\n".format(fpath))
            elif os.path.isdir(fpath) and not os.listdir(fpath):
                os.rmdir(fpath)
            else:
                ctx.ui.warning(_('Installed file {} does not exist on system [Probably you manually deleted]').format(fpath))
                return

        # remove emptied directories
        dpath = os.path.dirname(fpath)
        while dpath != '/' and not os.listdir(dpath):
            os.rmdir(dpath)
            dpath = os.path.dirname(dpath)

    def run_preremove(self):
        if ctx.scom:
            import inary.scomiface
            inary.scomiface.pre_remove(
                self.package_name,
                os.path.join(self.package.pkg_dir(), ctx.const.metadata_xml),
                os.path.join(self.package.pkg_dir(), ctx.const.files_xml),
            )

    def run_postremove(self):
        if ctx.scom:
            import inary.scomiface
            inary.scomiface.post_remove(
                self.package_name,
                os.path.join(self.package.pkg_dir(), ctx.const.metadata_xml),
                os.path.join(self.package.pkg_dir(), ctx.const.files_xml),
                provided_scripts=self.package.providesScom,
            )

    def update_databases(self):
        self.remove_db()
        self.historydb.add_and_update(pkgBefore=self.package, operation="remove")

    def remove_inary_files(self):
        util.clean_dir(self.package.pkg_dir())

    def remove_db(self):
        self.installdb.remove_package(self.package_name)
        ctx.filesdb.remove_files(self.files.list)
# FIX:DB
#         # FIXME: something goes wrong here, if we use ctx operations ends up with segmentation fault!
#         inary.db.packagedb.remove_tracking_package(self.package_name)


def remove_single(package_name):
    Remove(package_name).run()

def build(package):
    # wrapper for build op
    import inary.operations.build
    return inary.operations.build.build(package)

#API ORDERS
def locked(func):
    """
    Decorator for synchronizing privileged functions
    """
    def wrapper(*__args,**__kw):
        try:
            lock = open(util.join_path(ctx.config.lock_dir(), 'inary'), 'w')
        except IOError:
            raise inary.errors.PrivilegeError(_("You have to be root for this operation."))

        try:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            ctx.locked = True
        except IOError:
            if not ctx.locked:
                raise inary.errors.AnotherInstanceError(_("Another instance of Inary is running. Only one instance is allowed."))

        try:
            inary.db.invalidate_caches()
            ret = func(*__args,**__kw)
            inary.db.update_caches()
            return ret
        finally:
            ctx.locked = False
            lock.close()
    return wrapper


@locked
def upgrade(packages=[], repo=None):
    """
    Upgrades the given packages, if no package given upgrades all the packages
    @param packages: list of package names -> list_of_strings
    @param repo: name of the repository that only the packages from that repo going to be upgraded
    """
    inary.db.historydb.HistoryDB().create_history("upgrade")
    return inary.operations.upgrade.upgrade(packages, repo)

@locked
def remove(packages, ignore_dependency=False, ignore_safety=False):
    """
    Removes the given packages from the system
    @param packages: list of package names -> list_of_strings
    @param ignore_dependency: removes packages without looking into theirs reverse deps if True
    @param ignore_safety: system.base packages can also be removed if True
    """
    inary.db.historydb.HistoryDB().create_history("remove")
    return inary.operations.remove.remove(packages, ignore_dependency, ignore_safety)

@locked
def install(packages, reinstall=False, ignore_file_conflicts=False, ignore_package_conflicts=False):
    """
    Returns True if no errors occured during the operation
    @param packages: list of package names -> list_of_strings
    @param reinstall: reinstalls already installed packages else ignores
    @param ignore_file_conflicts: Ignores file conflicts during the installation and continues to install
    packages.
    @param ignore_package_conflicts: Ignores package conflicts during the installation and continues to
    install packages.
    """

    inary.db.historydb.HistoryDB().create_history("install")

    if not ctx.get_option('ignore_file_conflicts'):
        ctx.set_option('ignore_file_conflicts', ignore_file_conflicts)

    if not ctx.get_option('ignore_package_conflicts'):
        ctx.set_option('ignore_package_conflicts', ignore_package_conflicts)

    # Install inary package files or inary packages from a repository
    if packages and packages[0].endswith(ctx.const.package_suffix):
        return inary.operations.install.install_pkg_files(packages, reinstall)
    else:
        return inary.operations.install.install_pkg_names(packages, reinstall)

@locked
def takeback(operation):
    """
    Takes back the system to a previous state. Uses inary history to find out which packages were
    installed at the time _after_ the given operation that the system is requested to be taken back.
    @param operation: number of the operation that the system will be taken back -> integer
    """

    historydb = inary.db.historydb.HistoryDB()
    historydb.create_history("takeback")

    inary.operations.history.takeback(operation)


@locked
def set_repo_activity(name, active):
    """
    Changes the activity status of a  repository. Inactive repositories will have no effect on
    upgrades and installs.
    @param name: name of the repository
    @param active: the new repository status
    """
    repodb = inary.db.repodb.RepoDB()
    if active:
        repodb.activate_repo(name)
    else:
        repodb.deactivate_repo(name)
    inary.db.regenerate_caches()

@locked
def emerge(packages):
    """
    Builds and installs the given packages from source
    @param packages: list of package names -> list_of_strings
    """
    inary.db.historydb.HistoryDB().create_history("emerge")
    return inary.operations.emerge.emerge(packages)

@locked
def delete_cache():
    """
    Deletes cached packages, cached archives, build dirs, db caches
    """
    ctx.ui.info(_("Cleaning package cache {}...").format(ctx.config.cached_packages_dir()))
    util.clean_dir(ctx.config.cached_packages_dir())
    ctx.ui.info(_("Cleaning source archive cache {}...").format(ctx.config.archives_dir()))
    util.clean_dir(ctx.config.archives_dir())
    ctx.ui.info(_("Cleaning temporary directory {}...").format(ctx.config.tmp_dir()))
    util.clean_dir(ctx.config.tmp_dir())
    for cache in [x for x in os.listdir(ctx.config.cache_root_dir()) if x.endswith(".cache")]:
        cache_file = util.join_path(ctx.config.cache_root_dir(), cache)
        ctx.ui.info(_("Removing cache file {}...").format(cache_file))
        os.unlink(cache_file)

def check(package, config=False):
    """
    Returns a dictionary that contains a list of both corrupted and missing files
    @param package: name of the package to be checked
    @param config: _only_ check the config files of the package, default behaviour is to check all the files
    of the package but the config files
    """
    return inary.operations.check.check_package(package, config)

@locked
def snapshot():
    """
    Takes snapshot of the system packages. The snapshot is only a record of which packages are currently
    installed. The record is kept by inary history mechanism as it works automatically on install, remove
    and upgrade operations.
    """

    installdb = inary.db.installdb.InstallDB()
    historydb = inary.db.historydb.HistoryDB()
    historydb.create_history("snapshot")

    li = installdb.list_installed()
    progress = ctx.ui.Progress(len(li))

    processed = 0
    for name in installdb.list_installed():
        package = installdb.get_package(name)
        historydb.add_package(pkgBefore=package, operation="snapshot")
        # Save changed config files of the package in snapshot
        for f in installdb.get_files(name).list:
            if f.type == "config" and util.config_changed(f):
                fpath = util.join_path(ctx.config.dest_dir(), f.path)
                historydb.save_config(name, fpath)

        processed += 1
        ctx.ui.display_progress(operation = "snapshot",
                                percent = progress.update(processed),
                                info = _("Taking snapshot of the system"))

    historydb.update_history()

@locked
def configure_pending(packages=None):
    # Import SCOM
    import inary.scomiface

    # start with pending packages
    # configure them in reverse topological order of dependency
    installdb = inary.db.installdb.InstallDB()
    if not packages:
        packages = installdb.list_pending()
    else:
        packages = set(packages).intersection(installdb.list_pending())

    order = pgraph.generate_pending_order(packages)
    try:
        for x in order:
            if installdb.has_package(x):
                pkginfo = installdb.get_package(x)
                pkg_path = installdb.package_path(x)
                m = inary.data.metadata.MetaData()
                metadata_path = util.join_path(pkg_path, ctx.const.metadata_xml)
                m.read(metadata_path)
                # FIXME: we need a full package info here!
                pkginfo.name = x
                ctx.ui.notify(inary.ui.configuring, package = pkginfo, files = None)
                inary.scomiface.post_install(
                    pkginfo.name,
                    m.package.providesScom,
                    util.join_path(pkg_path, ctx.const.scom_dir),
                    util.join_path(pkg_path, ctx.const.metadata_xml),
                    util.join_path(pkg_path, ctx.const.files_xml),
                    None,
                    None,
                    m.package.version,
                    m.package.release
                )
                ctx.ui.notify(inary.ui.configured, package = pkginfo, files = None)
            installdb.clear_pending(x)
    except ImportError:
        raise inary.Error(_("scom package is not fully installed"))


@locked
def add_repo(name, indexuri, at = None):
    import re
    if not re.match("^[0-9{}\-\\_\\.\s]*$".format(str(util.letters())), name):
        raise inary.Error(_('Not a valid repo name.'))
    repodb = inary.db.repodb.RepoDB()
    if repodb.has_repo(name):
        raise inary.Error(_('Repo {} already present.').format(name))
    elif repodb.has_repo_url(indexuri, only_active = False):
        repo = repodb.get_repo_by_url(indexuri)
        raise inary.Error(_('Repo already present with name {}.').format(repo))
    else:
        repo = inary.db.repodb.Repo(inary.uri.URI(indexuri))
        repodb.add_repo(name, repo, at = at)
        inary.db.flush_caches()
        ctx.ui.info(_('Repo {} added to system.').format(name))

@locked
def remove_repo(name):
    repodb = inary.db.repodb.RepoDB()
    if repodb.has_repo(name):
        repodb.remove_repo(name)
        inary.db.flush_caches()
        ctx.ui.info(_('Repo {} removed from system.').format(name))
    else:
        raise inary.Error(_('Repository {} does not exist. Cannot remove.').format(name))

@locked
def update_repos(repos, force=False):
    inary.db.historydb.HistoryDB().create_history("repoupdate")
    updated = False
    try:
        for repo in repos:
            updated |= __update_repo(repo, force)
    finally:
        if updated:
            inary.db.regenerate_caches()

@locked
def update_repo(repo, force=False):
    inary.db.historydb.HistoryDB().create_history("repoupdate")
    updated = __update_repo(repo, force)
    if updated:
        inary.db.regenerate_caches()

def __update_repo(repo, force=False):
    ctx.ui.action(_('Updating repository: {}').format(repo))
    ctx.ui.notify(inary.ui.updatingrepo, name = repo)
    repodb = inary.db.repodb.RepoDB()
    index = inary.data.index.Index()
    if repodb.has_repo(repo):
        repouri = repodb.get_repo(repo).indexuri.get_uri()
        try:
            index.read_uri_of_repo(repouri, repo)
        except inary.file.AlreadyHaveException as e:
            ctx.ui.info(_('{} repository information is up-to-date.').format(repo))
            if force:
                ctx.ui.info(_('Updating database at any rate as requested'))
                index.read_uri_of_repo(repouri, repo, force = force)
            else:
                return False

        inary.db.historydb.HistoryDB().update_repo(repo, repouri, "update")
        repodb.check_distribution(repo)

        try:
            index.check_signature(repouri, repo)
        except inary.file.NoSignatureFound as e:
            ctx.ui.warning(e)

        ctx.ui.info(_('Package database updated.'))
    else:
        raise inary.Error(_('No repository named {} found.').format(repo))

    return True

# FIXME: rebuild_db is only here for filesdb and it really is ugly. we should not need any rebuild.
@locked
def rebuild_db():

    # save parameters and shutdown inary
    options = ctx.config.options
    ui = ctx.ui
    scom = ctx.scom
    inary._cleanup()

    ctx.filesdb.close()
    ctx.filesdb.destroy()
    ctx.filesdb = inary.db.filesdb.FilesDB()

    # reinitialize everything
    ctx.ui = ui
    ctx.config.set_options(options)
    ctx.scom = scom

@locked
def clearCache(all=False):

    import glob

    def getPackageLists(pkgList):
        latest = {}
        for f in pkgList:
            try:
                name, full_version = util.parse_package_name(f)
                version, release, build = util.split_version(full_version)

                release = int(release)
                if name in latest:
                    lversion, lrelease = latest[name]
                    if lrelease > release:
                        continue

                latest[name] = full_version, release

            except:
                pass

        latestVersions = []
        for pkg in latest:
            latestVersions.append("{0}-{1}".format(pkg, latest[pkg][0]))

        oldVersions = list(set(pkgList) - set(latestVersions))
        return oldVersions, latestVersions

    def getRemoveOrder(cacheDir, pkgList):
        sizes = {}
        for pkg in pkgList:
            sizes[pkg] = os.stat(os.path.join(cacheDir, pkg) + ctx.const.package_suffix).st_size

        # sort dictionary by value from PEP-265
        from operator import itemgetter
        return sorted(iter(sizes.items()), key=itemgetter(1), reverse=False)

    def removeOrderByLimit(cacheDir, order, limit):
        totalSize = 0
        for pkg, size in order:
            totalSize += size
            if totalSize >= limit:
                try:
                    os.remove(os.path.join(cacheDir, pkg) + ctx.const.package_suffix)
                except exceptions.OSError:
                    pass

    def removeAll(cacheDir):
        cached = glob.glob("{}/*.inary".format(cacheDir)) + glob.glob("{}/*.part".format(cacheDir))
        for pkg in cached:
            try:
                os.remove(pkg)
            except exceptions.OSError:
                pass

    cacheDir = ctx.config.cached_packages_dir()

    pkgList = [os.path.basename(x).split(ctx.const.package_suffix)[0] for x in glob.glob("{}/*.inary".format(cacheDir))]
    if not all:
        # Cache limits from inary.conf
        config = inary.configfile.ConfigurationFile("/etc/inary/inary.conf")
        cacheLimit = int(config.get("general", "package_cache_limit")) * 1024 * 1024 # is this safe?
        if not cacheLimit:
            return

        old, latest = getPackageLists(pkgList)
        order = getRemoveOrder(cacheDir, latest) + getRemoveOrder(cacheDir, old)
        removeOrderByLimit(cacheDir, order, cacheLimit)
    else:
        removeAll(cacheDir)

def reorder_base_packages(*args, **kw):
    return inary.operations.helper.reorder_base_packages(*args, **kw)
