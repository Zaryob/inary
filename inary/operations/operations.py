# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import fnctl

import inary
import inary.atomicoperations
import inary.context as ctx
import inary.db
import inary.data
import inary.errors
import inary.fetcher
import inary.file
import inary.operations
import inary.ui
import inary.util

#API ORDERS
def locked(func):
    """
    Decorator for synchronizing privileged functions
    """
    def wrapper(*__args,**__kw):
        try:
            lock = open(inary.util.join_path(ctx.config.lock_dir(), 'inary'), 'w')
        except IOError:
            raise inary.errors.PrivilegeError(_("You have to be root for this operation."))

        try:
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
    inary.util.clean_dir(ctx.config.cached_packages_dir())
    ctx.ui.info(_("Cleaning source archive cache {}...").format(ctx.config.archives_dir()))
    inary.util.clean_dir(ctx.config.archives_dir())
    ctx.ui.info(_("Cleaning temporary directory {}...").format(ctx.config.tmp_dir()))
    inary.util.clean_dir(ctx.config.tmp_dir())
    for cache in [x for x in os.listdir(ctx.config.cache_root_dir()) if x.endswith(".cache")]:
        cache_file = inary.util.join_path(ctx.config.cache_root_dir(), cache)
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
            if f.type == "config" and inary.util.config_changed(f):
                fpath = inary.util.join_path(ctx.config.dest_dir(), f.path)
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

    order = generate_pending_order(packages)
    try:
        for x in order:
            if installdb.has_package(x):
                pkginfo = installdb.get_package(x)
                pkg_path = installdb.package_path(x)
                m = inary.data.metadata.MetaData()
                metadata_path = inary.util.join_path(pkg_path, ctx.const.metadata_xml)
                m.read(metadata_path)
                # FIXME: we need a full package info here!
                pkginfo.name = x
                ctx.ui.notify(inary.ui.configuring, package = pkginfo, files = None)
                inary.scomiface.post_install(
                    pkginfo.name,
                    m.package.providesScom,
                    inary.util.join_path(pkg_path, ctx.const.scom_dir),
                    inary.util.join_path(pkg_path, ctx.const.metadata_xml),
                    inary.util.join_path(pkg_path, ctx.const.files_xml),
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
    if not re.match("^[0-9{}\-\\_\\.\s]*$".format(str(inary.util.letters())), name):
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
                name, full_version = inary.util.parse_package_name(f)
                version, release, build = inary.util.split_version(full_version)

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
