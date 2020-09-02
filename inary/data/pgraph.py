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

"""INARY package relation graph that represents the state of packagedb"""

# Inary Modules
import inary.db
from inary.errors import CycleException
import inary.context as ctx
import inary.operations.helper as op_helper

# Gettext Library
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class PGraph:

    def __init__(self, packagedb=None, installdb=None):
        self.packagedb = packagedb
        self.installdb = installdb
        self.packages = []
        self.vertic = []
        self.checked = []
        self.reinstall = False

        if not installdb:
            self.installdb = inary.db.installdb.InstallDB()

        if not packagedb:
            self.packagedb = inary.db.packagedb.PackageDB()

    def get_installdb(self):
        return self.installdb

    def get_packagedb(self):
        return self.packagedb

    def topological_sort(self):
        return inary.util.unique_list(self.packages)

    def check_package(self, pkg=None, reverse=False):
        if pkg not in self.checked:
            self.checked.append(pkg)
        else:
            return

        if pkg in self.packages:
            return
        else:

            if reverse:
                if pkg not in self.packages:
                    self.packages.append(pkg)
                for (dep, depinfo) in self.installdb.get_rev_deps(pkg):
                    if dep not in self.packages:
                        self.check_package(dep, reverse)
                        if self.installdb.has_package(dep):
                            self.packages.append(dep)
            else:
                if self.installdb.has_package(pkg) and not self.reinstall:
                    return
                if pkg not in self.packages:
                    self.packages.append(pkg)
                for dep in self.packagedb.get_package(pkg).runtimeDependencies():
                    if dep not in self.packages:
                        self.check_package(dep.package, reverse)
                        if not self.installdb.has_package(dep.package):
                            self.packages.append(dep.package)

    def add_package(self, package):
        self.check_package(package, False)

    def add_package_revdep(self, package):
        self.check_package(package, True)

    def add_package_file(self, pkg):
        self.packages.append(pkg)
        for dep in self.installdb.get_package(pkg).runtimeDependencies():
            if dep not in self.packages:
                self.check_package(dep.package)

    def vertices(self):
        return self.vertic

# ****** Danger Zone Below! Tressspassers' eyes will explode! ********** #


def package_graph(A, packagedb, ignore_installed=False, reverse=False):
    """Construct a package relations graph.

    Graph will contain all dependencies of packages A, if ignore_installed
    option is True, then only uninstalled deps will be added.

    """

    ctx.ui.debug('A = {}'.format(str(A)))

    # try to construct a inary graph of packages to
    # install / reinstall

    G_f = PGraph(packagedb)  # construct G_f

    # find the "install closure" graph of G_f by package
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    # state = {}
    while len(B) > 0:
        Bp = set()
        # print pkg
        if reverse:
            True
        else:
            for x in B:
                G_f.add_package(x)
        B = Bp
    return G_f


def generate_pending_order(A):
    # returns pending package list in reverse topological order of dependency
    installdb = inary.db.installdb.InstallDB()
    G_f = PGraph(installdb)  # construct G_f
    for x in A:
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            G_f.add_package(x)
        B = Bp
    order = G_f.topological_sort()
    order.reverse()

    componentdb = inary.db.componentdb.ComponentDB()
    # Bug 4211
    if componentdb.has_component('system.base'):
        order = op_helper.reorder_base_packages(order)

    return order
