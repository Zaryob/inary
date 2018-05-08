# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import gettext
__trans = gettext.translation("inary", fallback=True)
_ = __trans.gettext

import inary.errors
import inary.context as ctx
import inary.util
import inary.db
import inary.fetcher
import inary.operations

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
            configs.append((pkg, operation))
        else:
            if installdb.has_package(pkg):
                beremoved.append("{}".format(pkg))

    return beinstalled, beremoved, configs

def __getpackageurl(package):
    packagedb = inary.db.packagedb.PackageDB()
    repodb = inary.db.repodb.RepoDB()
    pkg, ver = inary.util.parse_package_name(package)

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
    ctx.ui.info(_("Package {0} found in repository {1}").format(pkg, reponame))

    #return _possible_ url for this package
    return os.path.join(os.path.dirname(repourl),
                        inary.util.parse_package_dir_path(package),
                        package)

def fetch_remote_file(package, errors):
    try:
        uri = inary.file.File.make_uri(__getpackageurl(package))
    except PackageNotFound:
        errors.append(package)
        ctx.ui.info(_("{} could not be found").format(package), color="red")
        return False

    dest = ctx.config.cached_packages_dir()
    filepath = os.path.join(dest, uri.filename())
    if not os.path.exists(filepath):
        try:
            inary.fetcher.fetch_url(uri, dest, ctx.ui.Progress)
        except inary.fetcher.FetchError as e:
            errors.append(package)
            ctx.ui.info(_("{} could not be found").format(package), color="red")
            return False
    else:
        ctx.ui.info(_('{} [cached]').format(uri.filename()))
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

def takeback(operation):
    historydb = inary.db.historydb.HistoryDB()
    beinstalled, beremoved, configs = plan_takeback(operation)

    if beinstalled:
        ctx.ui.info(_("Following packages will be installed:\n") + inary.util.strlist(beinstalled))

    if beremoved:
        ctx.ui.info(_("Following packages will be removed:\n") + inary.util.strlist(beremoved))

    if (beremoved or beinstalled) and not ctx.ui.confirm(_('Do you want to continue?')):
        return

    errors = []
    paths = []
    for pkg in beinstalled:
        ctx.ui.info(_("Downloading %d / %d") % (beinstalled.index(pkg)+1, len(beinstalled)), color="yellow")
        pkg += ctx.const.package_suffix
        if fetch_remote_file(pkg, errors):
            paths.append(os.path.join(ctx.config.cached_packages_dir(), pkg))

    if errors:
        ctx.ui.info(_("\nFollowing packages could not be found in repositories and are not cached:\n") +
                    inary.util.strlist(errors))
        if not ctx.ui.confirm(_('Do you want to continue?')):
            return

    if beremoved:
        inary.operations.remove.remove(beremoved, True, True)

    if paths:
        inary.operations.install.install_pkg_files(paths, True)

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
