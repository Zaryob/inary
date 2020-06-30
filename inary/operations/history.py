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

# Standart Python Libraries
import os
import math

# Inary Modules
import inary.db
import inary.errors
import inary.fetcher
import inary.util as util
import inary.context as ctx
import inary.operations as operations

# Gettext Library
import gettext
__trans = gettext.translation("inary", fallback=True)
_ = __trans.gettext


class PackageNotFound(inary.errors.Error):
    pass


def __pkg_already_installed(name, pkginfo):
    installdb = inary.db.installdb.InstallDB()
    if not installdb.has_package(name):
        return False

    ver, rel = str(pkginfo).split("-")[:2]
    return (ver, rel) == installdb.get_version(name)[:-1]


def __listactions(actions):
    beinstalled = []
    beremoved = []
    configs = []

    installdb = inary.db.installdb.InstallDB()
    for pkg in actions:
        action, pkginfo, operation = actions[pkg]
        if action == "install":
            if __pkg_already_installed(pkg, pkginfo):
                continue
            beinstalled.append("{0}-{1}".format(pkg, pkginfo))
            configs.append([pkg, operation])
        else:
            if installdb.has_package(pkg):
                beremoved.append("{}".format(pkg))

    return beinstalled, beremoved, configs


def __getpackageurl_binman(package):
    packagedb = inary.db.packagedb.PackageDB()
    repodb = inary.db.repodb.RepoDB()
    pkg = inary.util.parse_package_name_get_name(package)

    reponame = None
    try:
        reponame = packagedb.which_repo(pkg)
    except Exception:
        # Maybe this package is obsoluted from repository
        for repo in repodb.get_binary_repos():
            if pkg in packagedb.get_obsoletes(repo):
                reponame = repo

    if not reponame:
        raise PackageNotFound

    package_ = packagedb.get_package(pkg)
    repourl = repodb.get_repo_url(reponame)
    base_package = os.path.dirname(package_.packageURI)
    repo_base = os.path.dirname(repourl)
    possible_url = os.path.join(repo_base, base_package, package)
    ctx.ui.info(
        _("Package \"{0}\" found in repository \"{1}\".").format(
            pkg, reponame))

    # return _possible_ url for this package
    return possible_url


def __getpackageurl(package):
    packagedb = inary.db.packagedb.PackageDB()
    repodb = inary.db.repodb.RepoDB()
    pkg = util.parse_package_name_get_name(package)

    reponame = None
    try:
        reponame = packagedb.which_repo(pkg)
    except Exception:
        # Maybe this package is obsoluted from repository
        for repo in repodb.get_binary_repos():
            if pkg in packagedb.get_obsoletes(repo):
                reponame = repo

    if not reponame:
        raise PackageNotFound

    repourl = repodb.get_repo_url(reponame)
    ctx.ui.info(
        _("Package \"{0}\" found in repository \"{1}\".").format(
            pkg, reponame))

    # return _possible_ url for this package
    return os.path.join(os.path.dirname(repourl),
                        util.parse_package_dir_path(package),
                        package)


def fetch_remote_file(package, errors):
    try:
        uri = inary.file.File.make_uri(__getpackageurl_binman(package))
    except PackageNotFound:
        errors.append(package)
        ctx.ui.info(
            _("\"{}\" could not be found.").format(package),
            color="red")
        return False

    dest = ctx.config.cached_packages_dir()
    filepath = os.path.join(dest, uri.filename())
    if not os.path.exists(filepath):
        failed = True
        try:
            inary.fetcher.fetch_url(uri, dest, ctx.ui.Progress)
        except inary.fetcher.FetchError:
            errors.append(package)
            ctx.ui.info(
                _("\"{}\" could not be found.").format(package),
                color="red")
            failed = True
        if failed:
            try:
                new_uri = inary.file.File.make_uri(__getpackageurl(package))
                inary.fetcher.fetch_url(new_uri, dest, ctx.ui.Progress)
            except BaseException:
                errors.append(package)
                ctx.ui.info(
                    _("\"{}\" could not be found.").format(package), "red")
                return False

    else:
        ctx.ui.info(_('\"{}\" [cached]').format(uri.filename()))
    return True


def get_snapshot_actions(operation):
    actions = {}
    snapshot_pkgs = set()
    installdb = inary.db.installdb.InstallDB()

    for pkg in operation.packages:
        snapshot_pkgs.add(pkg.name)
        actions[pkg.name] = ("install", pkg.before, operation.no)

    for pkg in set(installdb.list_installed()) - snapshot_pkgs:
        actions[pkg] = ("remove", None, None)

    return actions


def get_takeback_actions(operation):
    actions = {}
    historydb = inary.db.historydb.HistoryDB()

    for operation in historydb.get_till_operation(operation):
        if operation.type == "snapshot":
            pass

        for pkg in operation.packages:
            if pkg.operation in ["upgrade", "downgrade", "remove"]:
                actions[pkg.name] = ("install", pkg.before, operation.no)
            if pkg.operation == "install":
                actions[pkg.name] = ("remove", None, operation.no)

    return actions


def plan_takeback(operation):
    historydb = inary.db.historydb.HistoryDB()
    op = historydb.get_operation(operation)
    if op.type == "snapshot":
        actions = get_snapshot_actions(op)
    else:
        actions = get_takeback_actions(operation)

    return __listactions(actions)


@util.locked
def takeback(operation):
    """
    Takes back the system to a previous state. Uses inary history to find out which packages were
    installed at the time _after_ the given operation that the system is requested to be taken back.
    @param operation: number of the operation that the system will be taken back -> integer
    """
    historydb = inary.db.historydb.HistoryDB()
    historydb.create_history("takeback")
    beinstalled, beremoved, configs = plan_takeback(operation)
    if not beinstalled and not beremoved:
        ctx.ui.info(
            _("There is no packages to taking back (installing or removing)."))
        return

    if beinstalled:
        ctx.ui.info(
            _("Following packages will be installed:\n") +
            util.strlist(beinstalled))

    if beremoved:
        ctx.ui.info(
            _("Following packages will be removed:\n") +
            util.strlist(beremoved))

    if (beremoved or beinstalled) and not ctx.ui.confirm(
            _('Would you like to continue?')):
        return

    errors = []
    paths = []
    for pkg in beinstalled:
        lndig = math.floor(math.log(len(beinstalled), 10)) + 1
        ctx.ui.info(_("Downloading") +
                    str(" [ {:>" +
                        str(lndig) +
                        "} / {} ] => [{}]").format(beinstalled.index(pkg) +
                                                   1, len(beinstalled), pkg), color="yellow")
        pkg += ctx.const.package_suffix
        if fetch_remote_file(pkg, errors):
            paths.append(os.path.join(ctx.config.cached_packages_dir(), pkg))

    if errors:
        ctx.ui.info(_("\nFollowing packages could not be found in repositories and are not cached:\n") +
                    util.strlist(errors))
        if not ctx.ui.confirm(_('Would you like to continue?')):
            return

    if beremoved:
        operations.remove.remove(beremoved, True, True)

    if paths:
        operations.install.install_pkg_files(paths, True)

    for pkg, operation in configs:
        historydb.load_config(operation, pkg)


def get_takeback_plan(operation):
    """
    Calculates and returns the plan of the takeback operation that contains information of which
    packages are going to be removed and which packages are going to be installed
    @param operation: number of the operation that the system will be taken back -> integer
    """

    beinstalled, beremoved, configs = plan_takeback(operation)
    return beinstalled, beremoved


@util.locked
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
        ctx.ui.display_progress(operation="snapshot",
                                percent=progress.update(processed),
                                info=_("Taking snapshot of the system."))
    ctx.ui.info("")
    historydb.update_history()
