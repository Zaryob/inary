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
#

# Standart Python Libraries
import os
import sys
import math
import zipfile

# Inary Modules
import inary.db
import inary.package
import inary.ui as ui
import inary.util as util
import inary.context as ctx
import inary.data.pgraph as pgraph
import inary.operations as operations
import inary.atomicoperations as atomicoperations

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


def install_pkg_names(A, reinstall=False, extra=False):
    """This is the real thing. It installs packages from
    the repository, trying to perform a minimum number of
    installs"""

    installdb = inary.db.installdb.InstallDB()
    packagedb = inary.db.packagedb.PackageDB()
    # A was a list, remove duplicates
    A_0 = A = set(A)

    # filter packages that are already installed
    if not reinstall:
        Ap = set([x for x in A if not installdb.has_package(x)])
        d = A - Ap
        if len(d) > 0:
            ctx.ui.warning(_("The following package(s) are already installed "
                             "and are not going to be installed again:"))
            ctx.ui.info(util.format_by_columns(sorted(d)))
            A = Ap

    if len(A) == 0:
        ctx.ui.info(_('No packages to install.'))
        return True

    A |= operations.upgrade.upgrade_base(A)
    if not ctx.config.get_option('ignore_dependency'):
        ctx.ui.info(
            _('Checking dependencies for install...'),
            color="brightpurple")
        order = plan_install_pkg_names(A, reinstall)
    else:
        order = list(A)
    componentdb = inary.db.componentdb.ComponentDB()

    # Bug 4211
    if componentdb.has_component('system.base'):
        order = operations.helper.reorder_base_packages(order)

    if len(order) > 1:
        ctx.ui.info(
            _("Following packages will be installed:"),
            color="brightblue")
        ctx.ui.info(util.format_by_columns(sorted(order)))

    operations.helper.calculate_download_sizes(order)
    operations.helper.calculate_free_space_needed(order)

    if ctx.get_option('dry_run'):
        return True

    extra_packages = set(order) - A_0
    if extra_packages:
        if not ctx.ui.confirm(
                _('There are extra packages due to dependencies. Would you like to continue?')):
            raise Exception(_('External dependencies not satisfied.'))

    ctx.ui.notify(ui.packagestogo, order=order)

    conflicts = []
    if not ctx.get_option('ignore_package_conflicts'):
        conflicts = operations.helper.check_conflicts(order, packagedb)

    paths = []
    extra_paths = {}
    try:
        lndig = math.floor(math.log(len(order), 10)) + 1
    except ValueError:
        lndig = 1
    for x in order:
        ctx.ui.info(
            _("Downloading") + str(" [ {:>" + str(lndig) + "} / {} ] => [{}]").format(order.index(x) + 1, len(order),
                                                                                      x), color="yellow")
        install_op = atomicoperations.Install.from_name(x)
        paths.append(install_op.package_fname)

        if x in extra_packages or (extra and x in A):
            extra_paths[install_op.package_fname] = x
        elif reinstall and x in installdb.installed_extra:
            installdb.installed_extra.remove(x)
            with open(os.path.join(ctx.config.info_dir(), ctx.const.installed_extra), "w") as ie_file:
                ie_file.write("\n".join(installdb.installed_extra) +
                              ("\n" if installdb.installed_extra else ""))
        ctx.ui.notify(ui.fetched, name=x)

    # fetch to be installed packages but do not install them.
    if ctx.get_option('fetch_only'):
        return

    if conflicts:
        operations.remove.remove_conflicting_packages(conflicts)

    for path in paths:
        if installdb.has_package(path):
            remove_op = atomicoperations.Remove(path)
            remove_op.run_preremove()
    for path in paths:
        install_op = atomicoperations.Install(path)
        install_op.store_postops()
        install_op.preinstall()

    for path in paths:
        install_op = atomicoperations.Install(path)
        ctx.ui.info(_("Installing") +
                    str(" [ {:>" +
                        str(lndig) +
                        "} / {} ]").format(paths.index(path) +
                                           1, len(paths)), color="yellow")
        install_op.store_inary_files()
        install_op.install(False)
        try:
            with open(os.path.join(ctx.config.info_dir(), ctx.const.installed_extra), "a") as ie_file:
                ie_file.write("{}\n".format(extra_paths[path]))
            installdb.installed_extra.append(extra_paths[path])
        except KeyError:
            pass

    for path in paths:
        install_op = atomicoperations.Install(path)
        install_op.postinstall()

    return True


def install_pkg_files(package_URIs, reinstall=False):
    """install a number of inary package files"""

    installdb = inary.db.installdb.InstallDB()
    ctx.ui.debug('A = {}'.format(str(package_URIs)))

    for x in package_URIs:
        if not x.endswith(ctx.const.package_suffix):
            raise Exception(
                _('Mixing file names and package names not supported yet.'))

    # filter packages that are already installed
    tobe_installed, already_installed = [], set()

    if not reinstall:
        for x in package_URIs:
            pkg_name = util.parse_package_name_get_name(
                os.path.basename(x))
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
            package = inary.package.Package(x)
            package.read()
        except zipfile.BadZipfile:
            # YALI needed to get which file is broken
            raise zipfile.BadZipfile(x)
        name = str(package.metadata.package.name)
        d_t[name] = package.metadata.package
        dfn[name] = x

    # check packages' DistributionReleases and Architecture
    if not ctx.get_option('ignore_check'):
        for x in list(d_t.keys()):
            pkg = d_t[x]
            if pkg.distributionRelease > ctx.config.values.general.distribution_release:
                raise Exception(_('Package \"{0}\" is not compatible with your distribution release \'{1}\' \'{2}\'.').format(
                    x, ctx.config.values.general.distribution,
                    ctx.config.values.general.distribution_release))
            if pkg.architecture != ctx.config.values.general.architecture:
                raise Exception(
                    _('Package \"{0}\" (\'{1}\') is not compatible with your \'{2}\' architecture.').format(x, pkg.architecture,
                                                                                                            ctx.config.values.general.architecture))

    def satisfiesDep(dep):
        # is dependency satisfied among available packages
        # or packages to be installed?
        return dep.satisfied_by_installed() or dep.satisfied_by_dict_repo(d_t)

    # for this case, we have to determine the dependencies
    # that aren't already satisfied and try to install them
    # from the repository
    dep_unsatis = []
    for name in list(d_t.keys()):
        pkg = d_t[name]
        deps = pkg.runtimeDependencies()
        for dep in deps:
            if not satisfiesDep(dep) and dep.package not in [
                    x.package for x in dep_unsatis]:
                dep_unsatis.append(dep)

    # now determine if these unsatisfied dependencies could
    # be satisfied by installing packages from the repo
    for dep in dep_unsatis:
        if not dep.satisfied_by_repo() and not ctx.config.get_option('ignore_satisfy'):
            raise Exception(
                _('External dependencies not satisfied: \"{}\", \"{}\"').format(dep, name))

    # if so, then invoke install_pkg_names
    extra_packages = [x.package for x in dep_unsatis]
    if extra_packages:
        ctx.ui.warning(_("The following packages will be installed "
                         "in order to satisfy dependencies:"))
        ctx.ui.info(util.format_by_columns(sorted(extra_packages)))
        if not ctx.ui.confirm(_('Would you like to continue?')):
            raise Exception(_('External dependencies not satisfied.'))
        install_pkg_names(extra_packages, reinstall=False, extra=False)

    class PackageDB:
        @staticmethod
        def get_package(key, repo=None):
            return d_t[str(key)]

    packagedb = PackageDB()
    installdb = inary.db.installdb.InstallDB()

    A = list(d_t.keys())

    if len(A) == 0:
        ctx.ui.info(_('No packages to install.'))
        return

    # try to construct a inary graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(packagedb, installdb)  # construct G_f
    G_f.reinstall = reinstall

    # find the "install closure" graph of G_f by package
    # set A using packagedb
    for x in A:
        G_f.packages.append(x)
    print(tobe_installed)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            G_f.add_package(x)
            # for dep in pkg.runtimeDependencies():
            #   G_f.add_package(dep)
        B = Bp
    order = G_f.topological_sort()
    if not ctx.get_option('ignore_package_conflicts'):
        conflicts = operations.helper.check_conflicts(order, packagedb)
        if conflicts:
            operations.remove.remove_conflicting_packages(conflicts)
    order.reverse()
    ctx.ui.info(_('Installation order: ') + util.strlist(order))

    if ctx.get_option('dry_run'):
        return True

    ctx.ui.notify(ui.packagestogo, order=order)

    for x in order:
        atomicoperations.install_single_file(dfn[x], reinstall)

    return True


def plan_install_pkg_names(A, reinstall=False):
    # try to construct a inary graph of packages to
    # install / reinstall
    packagedb = inary.db.packagedb.PackageDB()
    installdb = inary.db.installdb.InstallDB()

    G_f = pgraph.PGraph(packagedb, installdb)  # construct G_f
    G_f.reinstall = reinstall

    # find the "install closure" graph of G_f by package
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    not_satisfied = dict()
    while len(B) > 0:
        Bp = set()
        for x in B:
            G_f.add_package(x)

            if ctx.config.values.general.allow_docs:
                dep = x + ctx.const.doc_package_end
                if packagedb.has_package(dep):
                    Bp.add(dep)
                    G_f.add_package(dep)
            if ctx.config.values.general.allow_pages:
                dep = x + ctx.const.info_package_end
                if packagedb.has_package(dep):
                    Bp.add(dep)
                    G_f.add_package(dep)
            if ctx.config.values.general.allow_dbginfo:
                dep = x + ctx.const.debug_name_suffix
                if packagedb.has_package(dep):
                    Bp.add(dep)
                    G_f.add_package(dep)
            if ctx.config.values.general.allow_static:
                dep = x + ctx.const.static_name_suffix
                if packagedb.has_package(dep):
                    Bp.add(dep)
                    G_f.add_package(dep)
        B = Bp
    if not_satisfied:
        msg = _("Following packages are not satisfied:\n")
        for ns in not_satisfied:
            msg += (_(' -> \"{0}\" dependency(s) of package \"{1}\" is not satisfied.\n').format(
                not_satisfied[ns], ns))
        raise Exception(msg)
    order = G_f.topological_sort()
    order.reverse()
    return order


def get_install_order(packages):
    # LOOK: This function is important
    """
    Return a list of packages in the installation order with extra needed
    dependencies -> list_of_strings
    @param packages: list of package names -> list_of_strings
    """
    return plan_install_pkg_names(packages)


@util.locked
def install(packages, reinstall=False, ignore_file_conflicts=False,
            ignore_package_conflicts=False):
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
        return install_pkg_files(packages, reinstall)
    else:
        return install_pkg_names(packages, reinstall)
