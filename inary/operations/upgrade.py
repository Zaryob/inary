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
#

import sys

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary
import inary.ui as ui
import inary.context as ctx
import inary.data.pgraph as pgraph
import inary.atomicoperations as atomicoperations
import inary.operations as operations
import inary.util as util
import inary.db
import inary.blacklist


def check_update_actions(packages):
    installdb = inary.db.installdb.InstallDB()
    packagedb = inary.db.packagedb.PackageDB()

    actions = {}

    for package in packages:
        if not installdb.has_package(package):
            continue

        pkg = packagedb.get_package(package)
        version, release, build = installdb.get_version(package)
        pkg_actions = pkg.get_update_actions(release)

        for action_name, action_targets in list(pkg_actions.items()):
            item = actions.setdefault(action_name, [])
            for action_target in action_targets:
                item.append((package, action_target))

    has_actions = False

    if "serviceRestart" in actions:
        has_actions = True
        ctx.ui.warning(_("You must restart the following service(s) manually "
                         "for the updated software to take effect:"))
        for package, target in actions["serviceRestart"]:
            ctx.ui.info("    - {}".format(target))

    if "systemRestart" in actions:
        has_actions = True
        ctx.ui.warning(_("You must restart your system for the updates "
                         "in the following package(s) to take effect:"))
        for package, target in actions["systemRestart"]:
            ctx.ui.info("    - {}".format(package))

    return has_actions


def find_upgrades(packages, replaces):
    packagedb = inary.db.packagedb.PackageDB()
    installdb = inary.db.installdb.InstallDB()

    debug = ctx.config.get_option("debug")
    security_only = ctx.get_option('security_only')
    comparesha1sum = ctx.get_option('compare_sha1sum')

    Ap = []
    ds = []
    for i_pkg in packages:

        if i_pkg in list(replaces.keys()):
            # Replaced packages will be forced for upgrade, cause replaced packages are marked as obsoleted also. So we
            # pass them.
            continue

        if i_pkg.endswith(ctx.const.package_suffix):
            ctx.ui.info(_("Warning: package *name* ends with '.inary'"), verbose=True)

        if not installdb.has_package(i_pkg):
            ctx.ui.info(_('Package \"{}\" is not installed.').format(i_pkg), True)
            continue

        if not packagedb.has_package(i_pkg):
            ctx.ui.info(_('Package \"{}\" is not available in repositories.').format(i_pkg), True)
            continue

        pkg = packagedb.get_package(i_pkg)
        hash = installdb.get_install_tar_hash(i_pkg)
        (version, release, build, distro, distro_release) = installdb.get_version_and_distro_release(i_pkg)

        if security_only and not pkg.has_update_type("security", release):
            continue

        if pkg.distribution == distro and \
                inary.version.make_version(pkg.distributionRelease) > inary.version.make_version(distro_release):
            Ap.append(i_pkg)

        else:
            if int(release) < int(pkg.release):
                Ap.append(i_pkg)
            elif comparesha1sum and \
                    int(release) == int(pkg.release) and \
                    not pkg.installTarHash == hash:
                Ap.append(i_pkg)
                ds.append(i_pkg)
            else:
                ctx.ui.info(_('Package \"{0.name}\" is already at the latest release {0.release}.').format(
                    pkg), True)

    if debug and ds:
        ctx.ui.info(_('The following packages have different sha1sum:'))
        ctx.ui.info(util.format_by_columns(sorted(ds)))

    return Ap


@util.locked
def upgrade(A=None, repo=None):
    """Re-installs packages from the repository, trying to perform
    a minimum or maximum number of upgrades according to options.

    Upgrades the given packages, if no package given upgrades all the packages
    @param A: list of package names -> list_of_strings
    @param repo: name of the repository that only the packages from that repo going to be upgraded
    """
    if A is None:
        A = []
    inary.db.historydb.HistoryDB().create_history("upgrade")

    packagedb = inary.db.packagedb.PackageDB()
    installdb = inary.db.installdb.InstallDB()
    replaces = packagedb.get_replaces()
    if not A:
        # if A is empty, then upgrade all packages
        A = installdb.list_installed()

    if repo:
        repo_packages = set(packagedb.list_packages(repo))
        A = set(A).intersection(repo_packages)

    A_0 = A = set(A)
    Ap = find_upgrades(A, replaces)
    A = set(Ap)

    # Force upgrading of installed but replaced packages or else they will be removed (they are obsoleted also).
    # This is not wanted for a replaced driver package (eg. nvidia-X).
    A |= set(inary.util.flatten_list(list(replaces.values())))

    A |= upgrade_base(A)

    A = inary.blacklist.exclude_from(A, ctx.const.blacklist)

    if ctx.get_option('exclude_from'):
        A = inary.blacklist.exclude_from(A, ctx.get_option('exclude_from'))

    if ctx.get_option('exclude'):
        A = inary.blacklist.exclude(A, ctx.get_option('exclude'))

    ctx.ui.debug('A = {}'.format(str(A)))

    if len(A) == 0:
        ctx.ui.info(_('No packages to upgrade.'))
        return True

    ctx.ui.debug('A = {}'.format(str(A)))

    if not ctx.config.get_option('ignore_dependency'):
        G_f, order = plan_upgrade(A, replaces=replaces)
    else:
        G_f = None
        order = list(A)

    componentdb = inary.db.componentdb.ComponentDB()

    # Bug 4211
    if componentdb.has_component('system.base'):
        order = operations.helper.reorder_base_packages(order)

    ctx.ui.info(_('The following packages will be upgraded:'), color="green")
    ctx.ui.info(util.format_by_columns(sorted(order)))

    operations.helper.calculate_download_sizes(order)
    operations.helper.calculate_free_space_needed(order)
    

    needs_confirm = check_update_actions(order)

    # NOTE: replaces.values() was already flattened above, it can be reused
    if set(order) - A_0 - set(inary.util.flatten_list(list(replaces.values()))):
        ctx.ui.warning(_("There are extra packages due to dependencies."))
        needs_confirm = True

    if ctx.get_option('dry_run'):
        return

    if needs_confirm and \
            not ctx.ui.confirm(_("Would you like to continue?")):
        return False

    ctx.ui.notify(ui.packagestogo, order=order)

    conflicts = []
    if not ctx.get_option('ignore_package_conflicts'):
        conflicts = operations.helper.check_conflicts(order, packagedb)

    paths = []
    for x in order:
        ctx.ui.info(_("Downloading %d / %d") % (order.index(x) + 1, len(order)), color="yellow")
        install_op = atomicoperations.Install.from_name(x)
        paths.append(install_op.package_fname)

    # fetch to be upgraded packages but do not install them.
    if ctx.get_option('fetch_only'):
        return

    if conflicts:
        operations.remove.remove_conflicting_packages(conflicts)

    operations.remove.remove_obsoleted_packages()

    try:
        for path in paths:
            ctx.ui.info(_("Installing %d / %d") % (paths.index(path) + 1, len(paths)), color="yellow")
            install_op = atomicoperations.Install(path, ignore_file_conflicts=True)
            install_op.install(not ctx.get_option('compare_sha1sum'))
    except Exception as e:
        raise (e)


def plan_upgrade(A, force_replaced=True, replaces=None):
    # FIXME: remove force_replaced
    # try to construct a inary graph of packages to
    # install / reinstall

    packagedb = inary.db.packagedb.PackageDB()

    G_f = pgraph.PGraph(packagedb)  # construct G_f

    A = set(A)

    # Force upgrading of installed but replaced packages or else they will be removed (they are obsoleted also).
    # This is not wanted for a replaced driver package (eg. nvidia-X).
    #
    # FIXME: this is also not nice. this would not be needed if replaced packages are not written as obsoleted also.
    # But if they are not written obsoleted "inary index" indexes them
    if force_replaced:
        if replaces is None:
            replaces = packagedb.get_replaces()
        A |= set(inary.util.flatten_list(list(replaces.values())))

    # find the "install closure" graph of G_f by package
    # set A using packagedb
    for x in A:
        G_f.add_package(x)

    installdb = inary.db.installdb.InstallDB()

    def add_runtime_deps(pkg, Bp):
        for dep in pkg.runtimeDependencies():
            # add packages that can be upgraded
            if installdb.has_package(dep.package) and dep.satisfied_by_installed():
                continue

            if dep.satisfied_by_repo():
                if not dep.package in G_f.vertices():
                    Bp.add(str(dep.package))

                # Always add the dependency info although the dependant
                # package is already a member of this graph. Upgrade order
                # might change if the dependency info differs from the
                # previous ones.
                G_f.add_dep(pkg.name, dep)
            else:
                ctx.ui.error(_('Dependency \"{0}\" of \"{1}\" cannot be satisfied').format(dep, pkg.name))
                raise Exception(_("Upgrade is not possible."))

    def add_resolvable_conflicts(pkg, Bp):
        """Try to resolve conflicts by upgrading

        If a package B conflicts with an old version of package A and
        does not conflict with the new version of A, add A to the upgrade list.
        """
        for conflict in pkg.conflicts:
            if conflict.package in G_f.vertices():
                # Conflicting package is already in the upgrade list.
                continue

            if not inary.analyzer.conflict.installed_package_conflicts(conflict):
                # Conflicting package is not installed.
                # No need to deal with it.
                continue

            if not packagedb.has_package(conflict.package):
                # Conflicting package is not available in repo.
                # Installed package will be removed.
                continue

            new_pkg = packagedb.get_package(conflict.package)
            if conflict.satisfies_relation(new_pkg.version, new_pkg.release):
                # Package still conflicts with the repo package.
                # Installed package will be removed.
                continue

            # Upgrading the package will resolve conflict.
            # Add it to the upgrade list.
            Bp.add(conflict.package)
            G_f.add_package(conflict.package)

    def add_broken_revdeps(pkg, Bp):
        # Search reverse dependencies to see if anything
        # should be upgraded
        rev_deps = installdb.get_rev_deps(pkg.name)
        for rev_dep, depinfo in rev_deps:
            # add only installed but unsatisfied reverse dependencies
            if rev_dep in G_f.vertices() or depinfo.satisfied_by_repo():
                continue

            if is_upgradable(rev_dep):
                Bp.add(rev_dep)
                G_f.add_plain_dep(rev_dep, pkg.name)

    def add_needed_revdeps(pkg, Bp):
        # Search for reverse dependency update needs of to be upgraded packages
        # check only the installed ones.
        version, release, build = installdb.get_version(pkg.name)
        actions = pkg.get_update_actions(release)

        packages = actions.get("reverseDependencyUpdate")
        if packages:
            for target_package in packages:
                for name, dep in installdb.get_rev_deps(target_package):
                    if name in G_f.vertices() or not is_upgradable(name):
                        continue

                    Bp.add(name)
                    G_f.add_plain_dep(name, target_package)

    while A:
        Bp = set()

        for x in A:
            pkg = packagedb.get_package(x)

            add_runtime_deps(pkg, Bp)
            add_resolvable_conflicts(pkg, Bp)

            if installdb.has_package(x):
                add_broken_revdeps(pkg, Bp)
                add_needed_revdeps(pkg, Bp)

        A = Bp

    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)

    order = G_f.topological_sort()
    order.reverse()
    return G_f, order


def upgrade_base(A=None):
    if A is None:
        A = set()
    installdb = inary.db.installdb.InstallDB()
    componentdb = inary.db.componentdb.ComponentDB()
    if not ctx.config.values.general.ignore_safety and not ctx.get_option('ignore_safety'):
        if componentdb.has_component('system.base'):
            systembase = set(componentdb.get_union_component('system.base').packages)
            extra_installs = [x for x in systembase - set(A) if not installdb.has_package(x)]
            extra_installs = inary.blacklist.exclude_from(extra_installs, ctx.const.blacklist)
            if extra_installs:
                ctx.ui.warning(_("Safety switch forces the installation of "
                                 "following packages:"))
                ctx.ui.info(util.format_by_columns(sorted(extra_installs)))

            # Will delete G_F and extra_upgrades
            G_f, install_order = operations.install.plan_install_pkg_names(extra_installs)
            extra_upgrades = [x for x in systembase - set(install_order) if is_upgradable(x)]
            upgrade_order = []

            extra_upgrades = inary.blacklist.exclude_from(extra_upgrades, ctx.const.blacklist)

            if ctx.get_option('exclude_from'):
                extra_upgrades = inary.blacklist.exclude_from(extra_upgrades, ctx.get_option('exclude_from'))

            if ctx.get_option('exclude'):
                extra_upgrades = inary.blacklist.exclude(extra_upgrades, ctx.get_option('exclude'))

            if extra_upgrades:
                ctx.ui.warning(_("Safety switch forces the upgrade of "
                                 "following packages:"))
                ctx.ui.info(util.format_by_columns(sorted(extra_upgrades)))
                G_f, upgrade_order = plan_upgrade(extra_upgrades, force_replaced=False)

            # no-need-for-upgrade-order patch
            # extra_upgrades = filter(lambda x: is_upgradable(x, ignore_build), systembase - set(extra_installs))
            # return set(extra_installs + extra_upgrades)

            # return packages that must be added to any installation
            return set(install_order + upgrade_order)
        else:
            ctx.ui.warning(_('Safety switch: The component system.base cannot be found.'))
    return set()


def is_upgradable(name):
    installdb = inary.db.installdb.InstallDB()

    if not installdb.has_package(name):
        return False

    (i_version, i_release, i_build, i_distro, i_distro_release) = installdb.get_version_and_distro_release(name)

    packagedb = inary.db.packagedb.PackageDB()

    try:
        version, release, build, distro, distro_release = packagedb.get_version_and_distro_release(name,
                                                                                                   packagedb.which_repo(
                                                                                                       name))
    except KeyboardInterrupt:
        raise
    except Exception:  # FIXME: what exception could we catch here, replace with that.
        return False

    if distro == i_distro and \
            inary.version.make_version(distro_release) > inary.version.make_version(i_distro_release):
        return True

    return int(i_release) < int(release)


def get_upgrade_order(packages):
    """
    Return a list of packages in the upgrade order with extra needed
    dependencies -> list_of_strings
    @param packages: list of package names -> list_of_strings
    """
    upgrade_order = inary.operations.upgrade.plan_upgrade
    i_graph, order = upgrade_order(packages)
    return order


def get_base_upgrade_order(packages):
    """
    Return a list of packages of the system.base component that needs to be upgraded
    or installed in install order -> list_of_strings
    All the packages of the system.base component must be installed on the system
    @param packages: list of package names -> list_of_strings
    """
    upgrade_order = inary.operations.upgrade.upgrade_base
    order = upgrade_order(packages)
    return list(order)
