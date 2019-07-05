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
import sys

import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

import inary.atomicoperations as atomicoperations
import inary.context as ctx
import inary.data.pgraph as pgraph
import inary.db
import inary.errors
import inary.util as util
import inary.ui as ui


@util.locked
def remove(A, ignore_dep=False, ignore_safety=False):
    """
    Removes the given packages from the system
    @param A: list of package names -> list_of_strings
    @param ignore_dep: removes packages without looking into theirs reverse deps if True
    @param ignore_safety: system.base packages can also be removed if True
    """
    inary.db.historydb.HistoryDB().create_history("remove")
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
                raise inary.errors.Error(_("Safety switch prevents the removal of "
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
            ctx.ui.info(_('Package {} does not exist. Cannot remove.').format(x))
    A = set(Ap)

    if len(A) == 0:
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

    ctx.ui.notify(ui.packagestogo, order=order)

    for x in order:
        if installdb.has_package(x):
            atomicoperations.remove_single(x)
            if x in installdb.installed_extra:
                installdb.installed_extra.remove(x)
                with open(os.path.join(ctx.config.info_dir(), ctx.const.installed_extra), "w") as ie_file:
                    ie_file.write("\n".join(installdb.installed_extra) + ("\n" if installdb.installed_extra else ""))

        else:
            ctx.ui.info(_('Package {} is not installed. Cannot remove.').format(x))


def plan_remove(A):
    # try to construct a inary graph of packages to
    # install / reinstall

    installdb = inary.db.installdb.InstallDB()
    packagedb = inary.db.packagedb.PackageDB()

    G_f = pgraph.PGraph(installdb)  # construct G_f

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
                if installdb.has_package(
                        rev_dep) and depinfo.satisfied_by_installed() and not depinfo.satisfied_by_any_installed_other_than(
                        x):
                    if not rev_dep in G_f.vertices():
                        Bp.add(rev_dep)
                        G_f.add_plain_dep(rev_dep, x)
                    if ctx.config.values.general.allow_docs:
                        doc_package = x + ctx.const.doc_package_end
                        if packagedb.has_package(doc_package):
                            Bp.add(doc_package)

                    if ctx.config.values.general.allow_pages:
                        info_package = x + ctx.const.info_package_end
                        if packagedb.has_package(info_package):
                            Bp.add(info_package)

                    if ctx.config.values.general.allow_dbginfo:
                        dbg_package = x + ctx.const.debug_name_suffix
                        if packagedb.has_package(dbg_package):
                            Bp.add(dbg_package)

                    if ctx.config.values.general.allow_static:
                        static_package = x + ctx.const.static_name_suffix
                        if packagedb.has_package(static_package):
                            Bp.add(static_package)

        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.sort(True)
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


def get_remove_order(packages):
    """
    Return a list of packages in the remove order -> list_of_strings
    @param packages: list of package names -> list_of_strings
    """
    i_graph, order = plan_remove(packages)
    return order
