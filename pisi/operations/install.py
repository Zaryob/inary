# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 - 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import sys
import zipfile

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
import pisi.util as util
import pisi.atomicoperations as atomicoperations
import pisi.operations as operations
import pisi.pgraph as pgraph
import pisi.ui as ui
import pisi.db

def install_pkg_names(A, reinstall = False):
    """This is the real thing. It installs packages from
    the repository, trying to perform a minimum number of
    installs"""

    installdb = pisi.db.installdb.InstallDB()
    packagedb = pisi.db.packagedb.PackageDB()

    A = [str(x) for x in A] #FIXME: why do we still get unicode input here? :/ -- exa
    # A was a list, remove duplicates
    A_0 = A = set(A)

    # filter packages that are already installed
    if not reinstall:
        Ap = set(filter(lambda x: not installdb.has_package(x), A))
        d = A - Ap
        if len(d) > 0:
            ctx.ui.warning(_("The following package(s) are already installed "
                             "and are not going to be installed again:"))
            ctx.ui.info(util.format_by_columns(sorted(d)))
            A = Ap

    if len(A)==0:
        ctx.ui.info(_('No packages to install.'))
        return True

    A |= operations.upgrade.upgrade_base(A)

    if not ctx.config.get_option('ignore_dependency'):
        G_f, order = plan_install_pkg_names(A)
    else:
        G_f = None
        order = list(A)

    componentdb = pisi.db.componentdb.ComponentDB()

    # Bug 4211
    if componentdb.has_component('system.base'):
        order = operations.helper.reorder_base_packages(order)

    if len(order) > 1:
        ctx.ui.info(util.colorize(_("Following packages will be installed:"), "brightblue"))
        ctx.ui.info(util.format_by_columns(sorted(order)))

    total_size, cached_size = operations.helper.calculate_download_sizes(order)
    total_size, symbol = util.human_readable_size(total_size)
    ctx.ui.info(util.colorize(_('Total size of package(s): %.2f %s') % (total_size, symbol), "yellow"))

    if ctx.get_option('dry_run'):
        return True

    if set(order) - A_0:
        if not ctx.ui.confirm(_('There are extra packages due to dependencies. Do you want to continue?')):
            return False

    ctx.ui.notify(ui.packagestogo, order = order)

    ignore_dep = ctx.config.get_option('ignore_dependency')

    conflicts = []
    if not ctx.get_option('ignore_package_conflicts'):
        conflicts = operations.helper.check_conflicts(order, packagedb)

    paths = []
    for x in order:
        ctx.ui.info(util.colorize(_("Downloading %d / %d") % (order.index(x)+1, len(order)), "yellow"))
        install_op = atomicoperations.Install.from_name(x)
        paths.append(install_op.package_fname)

    # fetch to be installed packages but do not install them.
    if ctx.get_option('fetch_only'):
        return

    if conflicts:
        operations.remove.remove_conflicting_packages(conflicts)

    for path in paths:
        ctx.ui.info(util.colorize(_("Installing %d / %d") % (paths.index(path)+1, len(paths)), "yellow"))
        install_op = atomicoperations.Install(path)
        install_op.install(False)

    return True

def install_pkg_files(package_URIs, reinstall = False):
    """install a number of pisi package files"""

    installdb = pisi.db.installdb.InstallDB()
    ctx.ui.debug('A = %s' % str(package_URIs))

    for x in package_URIs:
        if not x.endswith(ctx.const.package_suffix):
            raise Exception(_('Mixing file names and package names not supported yet.'))

    # filter packages that are already installed
    tobe_installed, already_installed = [], set()
    if not reinstall:
        for x in package_URIs:
            if not x.endswith(ctx.const.delta_package_suffix) and x.endswith(ctx.const.package_suffix):
                pkg_name, pkg_version = pisi.util.parse_package_name(os.path.basename(x))
                if installdb.has_package(pkg_name):
                    already_installed.add(pkg_name)
                else:
                    tobe_installed.append(x)
        if already_installed:
            ctx.ui.warning(_("The following package(s) are already installed "
                             "and are not going to be installed again:"))
            ctx.ui.info(util.format_by_columns(sorted(already_installed)))
        package_URIs = tobe_installed

    if ctx.config.get_option('ignore_dependency'):
        # simple code path then
        for x in package_URIs:
            atomicoperations.install_single_file(x, reinstall)
        return True

    # read the package information into memory first
    # regardless of which distribution they come from
    d_t = {}
    dfn = {}
    for x in package_URIs:
        try:
            package = pisi.package.Package(x)
            package.read()
        except zipfile.BadZipfile:
            # YALI needed to get which file is broken
            raise zipfile.BadZipfile(x)
        name = str(package.metadata.package.name)
        d_t[name] = package.metadata.package
        dfn[name] = x

    # check packages' DistributionReleases and Architecture
    if not ctx.get_option('ignore_check'):
        for x in d_t.keys():
            pkg = d_t[x]
            if pkg.distributionRelease != ctx.config.values.general.distribution_release:
                raise Exception(_('Package %s is not compatible with your distribution release %s %s.') \
                        % (x, ctx.config.values.general.distribution, \
                        ctx.config.values.general.distribution_release))
            if pkg.architecture != ctx.config.values.general.architecture:
                raise Exception(_('Package %s (%s) is not compatible with your %s architecture.') \
                        % (x, pkg.architecture, ctx.config.values.general.architecture))

    def satisfiesDep(dep):
        # is dependency satisfied among available packages
        # or packages to be installed?
        return dep.satisfied_by_installed() or dep.satisfied_by_dict_repo(d_t)

    # for this case, we have to determine the dependencies
    # that aren't already satisfied and try to install them
    # from the repository
    dep_unsatis = []
    for name in d_t.keys():
        pkg = d_t[name]
        deps = pkg.runtimeDependencies()
        for dep in deps:
            if not satisfiesDep(dep) and dep.package not in [x.package for x in dep_unsatis]:
                dep_unsatis.append(dep)

    # now determine if these unsatisfied dependencies could
    # be satisfied by installing packages from the repo
    for dep in dep_unsatis:
        if not dep.satisfied_by_repo():
            raise Exception(_('External dependencies not satisfied: %s') % dep)

    # if so, then invoke install_pkg_names
    extra_packages = [x.package for x in dep_unsatis]
    if extra_packages:
        ctx.ui.warning(_("The following packages will be installed "
                         "in order to satisfy dependencies:"))
        ctx.ui.info(util.format_by_columns(sorted(extra_packages)))
        if not ctx.ui.confirm(_('Do you want to continue?')):
            raise Exception(_('External dependencies not satisfied'))
        install_pkg_names(extra_packages, reinstall=True)

    class PackageDB:
        def get_package(self, key, repo = None):
            return d_t[str(key)]

    packagedb = PackageDB()

    A = d_t.keys()

    if len(A)==0:
        ctx.ui.info(_('No packages to install.'))
        return

    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(packagedb)               # construct G_f

    # find the "install closure" graph of G_f by package
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            for dep in pkg.runtimeDependencies():
                if dep.satisfied_by_dict_repo(d_t):
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    if not ctx.get_option('ignore_package_conflicts'):
        conflicts = operations.helper.check_conflicts(order, packagedb)
        if conflicts:
            operations.remove.remove_conflicting_packages(conflicts)
    order.reverse()
    ctx.ui.info(_('Installation order: ') + util.strlist(order) )

    if ctx.get_option('dry_run'):
        return True

    ctx.ui.notify(ui.packagestogo, order = order)

    for x in order:
        atomicoperations.install_single_file(dfn[x], reinstall)

    return True

def plan_install_pkg_names(A):
    # try to construct a pisi graph of packages to
    # install / reinstall

    packagedb = pisi.db.packagedb.PackageDB()

    G_f = pgraph.PGraph(packagedb)               # construct G_f

    # find the "install closure" graph of G_f by package
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A

    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            for dep in pkg.runtimeDependencies():
                ctx.ui.debug('checking %s' % str(dep))
                # we don't deal with already *satisfied* dependencies
                if not dep.satisfied_by_installed():
                    if not dep.satisfied_by_repo():
                        raise Exception(_('%s dependency of package %s is not satisfied') % (dep, pkg.name))
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    return G_f, order
