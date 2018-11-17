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

import os

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.context as ctx
import inary.util as util
import inary.ui as ui
import inary.analyzer.conflict
import inary.db

def reorder_base_packages(order):

    componentdb = inary.db.componentdb.ComponentDB()

    """system.base packages must be first in order"""
    systembase = componentdb.get_union_component('system.base').packages

    systembase_order = []
    nonbase_order = []
    for pkg in order:
        if pkg in systembase:
            systembase_order.append(pkg)
        else:
            nonbase_order.append(pkg)

    return systembase_order + nonbase_order

def check_conflicts(order, packagedb):
    """check if upgrading to the latest versions will cause havoc
    done in a simple minded way without regard for dependencies of
    conflicts, etc."""

    (C, D, pkg_conflicts) = inary.analyzer.conflict.calculate_conflicts(order, packagedb)

    if D:
        raise Exception(_("Selected packages [{}] are in conflict with each other.").format(util.strlist(list(D))))

    if pkg_conflicts:
        conflicts = ""
        for pkg in list(pkg_conflicts.keys()):
            conflicts += _("[{0} conflicts with: {1}]\n").format(pkg, util.strlist(pkg_conflicts[pkg]))

        ctx.ui.info(_("The following packages have conflicts:\n{}").format(conflicts))

        if not ctx.ui.confirm(_('Remove the following conflicting packages?')):
            raise Exception(_("Conflicting packages should be removed to continue"))

    return list(C)

def expand_src_components(A):
    componentdb = inary.db.componentdb.ComponentDB()
    Ap = set()
    for x in A:
        if componentdb.has_component(x):
            Ap = Ap.union(componentdb.get_union_component(x).sources)
        else:
            Ap.add(x)
    return Ap

def calculate_download_sizes(order):
    total_size = cached_size = 0

    installdb = inary.db.installdb.InstallDB()
    packagedb = inary.db.packagedb.PackageDB()

    try:
        cached_packages_dir = ctx.config.cached_packages_dir()
    except OSError:
        # happens when cached_packages_dir tried to be created by an unpriviledged user
        cached_packages_dir = None

    for pkg in [packagedb.get_package(name) for name in order]:

        delta = None
        if installdb.has_package(pkg.name):
            (version, release, build, distro, distro_release) = installdb.get_version_and_distro_release(pkg.name)
            # inary distro upgrade should not use delta support
            if distro == pkg.distribution and distro_release == pkg.distributionRelease:
                delta = pkg.get_delta(release)

        ignore_delta = ctx.config.values.general.ignore_delta

        if delta and not ignore_delta:
            fn = os.path.basename(delta.packageURI)
            pkg_hash = delta.packageHash
            pkg_size = delta.packageSize
        else:
            fn = os.path.basename(pkg.packageURI)
            pkg_hash = pkg.packageHash
            pkg_size = pkg.packageSize

        if cached_packages_dir:
            path = util.join_path(cached_packages_dir, fn)
            # check the file and sha1sum to be sure it _is_ the cached package
            if os.path.exists(path) and util.sha1_file(path) == pkg_hash:
                cached_size += pkg_size
            elif os.path.exists("{}.part".format(path)):
                cached_size += os.stat("{}.part".format(path)).st_size

        total_size += pkg_size

    ctx.ui.notify(ui.cached, total=total_size, cached=cached_size)
    return total_size, cached_size

def get_package_requirements(packages):
    """
    Returns a dict with two keys - systemRestart, serviceRestart - with package lists as their values
    @param packages: list of package names -> list_of_strings

    >>> lu = inary.api.list_upgrades()

    >>> requirements = inary.api.get_package_requirements(lu)

    >>> print requirements
    >>> { "systemRestart":["kernel", "module-alsa-driver"], "serviceRestart":["mysql-server", "memcached", "postfix"] }

    """

    actions = ("systemRestart", "serviceRestart")
    requirements = dict((action, []) for action in actions)

    installdb = inary.db.installdb.InstallDB()
    packagedb = inary.db.packagedb.PackageDB()

    for i_pkg in packages:
        try:
            pkg = packagedb.get_package(i_pkg)
        except Exception: #FIXME: Should catch RepoItemNotFound exception
            pass

        version, release, build = installdb.get_version(i_pkg)
        pkg_actions = pkg.get_update_actions(release)

        for action_name in pkg_actions:
            if action_name in actions:
                requirements[action_name].append(pkg.name)

    return requirements
