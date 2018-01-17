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
#

import os
import sys

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary
import inary.context as ctx
import inary.atomicoperations as atomicoperations
import inary.data.pgraph as pgraph
import inary.util as util
import inary.ui as ui
import inary.db

def remove(A, ignore_dep = False, ignore_safety = False):
    """remove set A of packages from system (A is a list of package names)"""

    componentdb = inary.db.componentdb.ComponentDB()
    installdb = inary.db.installdb.InstallDB()

    A = [str(x) for x in A]

    # filter packages that are not installed
    A_0 = A = set(A)

    if not ctx.get_option('ignore_safety') and not ctx.config.values.general.ignore_safety and not ignore_safety:
        if componentdb.has_component('system.base'):
            systembase = set(componentdb.get_union_component('system.base').packages)
            refused = A.intersection(systembase)
            if refused:
                raise inary.Error(_("Safety switch prevents the removal of "
                                   "following packages:\n") +
                                    util.format_by_columns(sorted(refused)))
                A = A - systembase
        else:
            ctx.ui.warning(_("Safety switch: The component system.base cannot be found."))

    Ap = []
    for x in A:
        if installdb.has_package(x):
            Ap.append(x)
        else:
            ctx.ui.info(_('Package %s does not exist. Cannot remove.') % x)
    A = set(Ap)

    if len(A)==0:
        ctx.ui.info(_('No packages to remove.'))
        return False

    if not ctx.config.get_option('ignore_dependency') and not ignore_dep:
        G_f, order = plan_remove(A)
    else:
        G_f = None
        order = A

    ctx.ui.info(_("""The following list of packages will be removed
in the respective order to satisfy dependencies:
""") + util.strlist(order))
    if len(order) > len(A_0):
        if not ctx.ui.confirm(_('Do you want to continue?')):
            ctx.ui.warning(_('Package removal declined'))
            return False

    if ctx.get_option('dry_run'):
        return

    ctx.ui.notify(ui.packagestogo, order = order)

    for x in order:
        if installdb.has_package(x):
            atomicoperations.remove_single(x)
            if x in installdb.installed_extra:
                installdb.installed_extra.remove(x)
                with open(os.path.join(ctx.config.info_dir(), ctx.const.installed_extra), "w") as ie_file:
                    ie_file.write("\n".join(installdb.installed_extra) + ("\n" if installdb.installed_extra else ""))

        else:
            ctx.ui.info(_('Package %s is not installed. Cannot remove.') % x)

def plan_remove(A):
    # try to construct a inary graph of packages to
    # install / reinstall

    installdb = inary.db.installdb.InstallDB()

    G_f = pgraph.PGraph(installdb)               # construct G_f

    # find the (install closure) graph of G_f by package
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            rev_deps = installdb.get_rev_deps(x)
            for (rev_dep, depinfo) in rev_deps:
                # we don't deal with uninstalled rev deps
                # and unsatisfied dependencies (this is important, too)
                # satisfied_by_any_installed_other_than is for AnyDependency
                if installdb.has_package(rev_dep) and depinfo.satisfied_by_installed() and not depinfo.satisfied_by_any_installed_other_than(x):
                    if not rev_dep in G_f.vertices():
                        Bp.add(rev_dep)
                        G_f.add_plain_dep(rev_dep, x)
        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    return G_f, order

def remove_conflicting_packages(conflicts):
    if remove(conflicts, ignore_dep=True, ignore_safety=True):
        raise Exception(_("Conflicts remain"))

def remove_obsoleted_packages():
    installdb = inary.db.installdb.InstallDB()
    packagedb = inary.db.packagedb.PackageDB()
    obsoletes = list(filter(installdb.has_package, packagedb.get_obsoletes()))
    if obsoletes:
        if remove(obsoletes, ignore_dep=True, ignore_safety=True):
            raise Exception(_("Obsoleted packages remaining"))

def remove_replaced_packages(replaced):
    if remove(replaced, ignore_dep=True, ignore_safety=True):
        raise Exception(_("Replaced package remains"))
