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

"""INARY package relation graph that represents the state of packagedb"""

import inary.context as ctx
import inary.db
import inary.errors
import inary.operations.helper as op_helper
import inary.util as util
import inary.misc.sort as sort

import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class CycleException(inary.errors.Exception):
    def __init__(self, cycle):
        self.cycle = cycle

    def __str__(self):
        return _('Encountered cycle {}').format(self.cycle)


class Digraph(object):

    def __init__(self):
        self.__v = set()
        self.__adj = {}
        self.__vdata = {}
        self.__edata = {}

    def vertices(self):
        """return set of vertex descriptors"""
        return self.__v

    def edges(self):
        """return a list of edge descriptors"""
        l = []
        for u in self.__v:
            for v in self.__adj[u]:
<<<<<<< HEAD
                l.append((u, v))
        return l

    def add_vertex(self, u, data=None):
        """add vertex u, optionally with data"""
        if not u in self.__v:
            self.__v.add(u)
            self.__adj[u] = set()
            if data:
                self.__vdata[u] = data
                self.__edata[u] = {}

    def add_edge(self, u, v, edata=None, udata=None, vdata=None):
        """add edge u -> v"""
        if not u in self.__v:
            self.add_vertex(u, udata)
        if not v in self.__v:
            self.add_vertex(v, vdata)
        self.__adj[u].add(v)
        if edata is not None:
            self.__edata[u][v] = edata
=======
                l.append( (u,v) )
                return l

    def add_vertex(self, u, data = None):
        """add vertex u, optionally with data"""
        assert not u in self.__v
        self.__v.add(u)
        self.__adj[u] = set()
        if data:
            self.__vdata[u] = data
            self.__edata[u] = {}

    def add_edge(self, u, v, edata = None, udata = None, vdata = None):
        """add edge u -> v"""
        if not u in self.__v:
            self.add_vertex(u, udata)
            if not v in self.__v:
                self.add_vertex(v, vdata)
                self.__adj[u].add(v)
                if edata is not None:
                    self.__edata[u][v] = edata
>>>>>>> master

    def add_biedge(self, u, v, edata=None):
        self.add_edge(u, v, edata)
        self.add_edge(v, u, edata)

    def set_vertex_data(self, u, data):
        self.__vdata[u] = data

    def vertex_data(self, u):
        return self.__vdata[u]

    def edge_data(self, u, v):
        return self.__edata[u][v]

    def has_vertex(self, u):
        return u in self.__v

    def has_edge(self, u, v):
        if u in self.__v:
            return v in self.__adj[u]
        else:
            return False

    def adj(self, u):
        return self.__adj[u]

<<<<<<< HEAD
    def get_vertex(self):
=======
    def dfs(self, finish_hook = None):
        self.color = {}
        self.p = {}
        self.d = {}
        self.f = {}
        for u in self.__v:
            self.color[u] = 'w'         # mark white (unexplored)
            self.p[u] = None
        self.time = 0
        for u in self.__v:
            if self.color[u] == 'w':
                self.dfs_visit(u, finish_hook)

    def dfs_visit(self, u, finish_hook):
        self.color[u] = 'g'             # mark green (discovered)
        self.d[u] = self.time = self.time + 1
        for v in self.adj(u):
            if self.color[v] == 'w':    # explore unexplored vertices
                self.p[v] = u
                self.dfs_visit(v, finish_hook)
            elif self.color[v] == 'g':  # cycle detected
                cycle = [u]
                while self.p[u]:
                    u = self.p[u]
                    cycle.append(u)
                    if self.has_edge(cycle[0], u):
                        break
                cycle.reverse()
                raise CycleException(cycle)
        self.color[u] = 'b'             # mark black (completed)
        if finish_hook:
            finish_hook(u)
            self.f[u] = self.time = self.time + 1

    def cycle_free(self):
        try:
            self.dfs()
            return True
        except CycleException:
            return False

    def topological_sort(self):
>>>>>>> master
        list = []
        for u in self.__v:
            list.append(u)
        return util.uniq(list)

<<<<<<< HEAD
    def sort(self,reverse=False):
            return sort.sort_auto(self.get_vertex(),reverse)
=======
>>>>>>> master
    @staticmethod
    def id_str(u):
        # Graph format only accepts underscores as key values
        # Sanitize the values. This is 2x faster than the old method.
        return u.replace("-", "_").replace("+", "_")

    def write_graphviz(self, f):
        f.write('digraph G {\n')
        for u in self.vertices():
            f.write(self.id_str(u))
            self.write_graphviz_vlabel(f, u)
            f.write(';\n')
        f.write('\n')
        for u in self.vertices():
            for v in self.adj(u):
<<<<<<< HEAD
                f.write(self.id_str(u) + ' -> ' + self.id_str(v))
=======
                f.write( self.id_str(u) + ' -> ' + self.id_str(v))
>>>>>>> master
                self.write_graphviz_elabel(f, u, v)
                f.write(';\n')
        f.write('\n')
        f.write('}\n')

    def write_graphviz_vlabel(self, f, u):
        pass

    def write_graphviz_elabel(self, f, u, v):
        pass


# Cache the results from packagedb queries in a graph

class PGraph(Digraph):

    def __init__(self, packagedb):
        super(PGraph, self).__init__()
        self.packagedb = packagedb

    def add_package(self, pkg):
        ctx.ui.debug(_("Package {} added in list.".format(pkg)))
        pkg1 = self.packagedb.get_package(pkg)
        self.add_vertex(str(pkg), (pkg1.version, pkg1.release))

    def add_plain_dep(self, pkg1name, pkg2name):
        pkg1data = None
        if not pkg1name in self.vertices():
            pkg1 = self.packagedb.get_package(pkg1name)
            pkg1data = (pkg1.version, pkg1.release)
        pkg2data = None
        if not pkg2name in self.vertices():
            pkg2 = self.packagedb.get_package(pkg2name)
            pkg2data = (pkg2.version, pkg2.release)
        self.add_edge(str(pkg1name), str(pkg2name), ('d', None),
                      pkg1data, pkg2data)

    def add_dep(self, pkg, depinfo):
        pkg1data = None
        if not pkg in self.vertices():
            pkg1 = self.packagedb.get_package(pkg)
            pkg1data = (pkg1.version, pkg1.release)
        pkg2data = None
        if not depinfo.package in self.vertices():
            pkg2 = self.packagedb.get_package(depinfo.package)
            pkg2data = (pkg2.version, pkg2.release)
        self.add_edge(str(pkg), str(depinfo.package), ('d', depinfo),
                      pkg1data, pkg2data)

    def write_graphviz_vlabel(self, f, u):
        (v, r) = self.vertex_data(u)
        f.write('[ label = \"' + str(u) + '(' + str(v) + ',' + str(r) + ')\" ]')


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
        for x in B:
            pkg = packagedb.get_package(x)
            # print pkg
            if reverse:
                for name, dep in packagedb.get_rev_deps(x):
                    if ignore_installed:
                        if dep.satisfied_by_installed():
                            continue
                    if not name in G_f.vertices():
                        Bp.add(name)
                    G_f.add_dep(name, dep)
            else:
                for dep in pkg.runtimeDependencies():
                    if ignore_installed:
                        if dep.satisfied_by_installed():
                            continue
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    return G_f


def generate_pending_order(A,installdb=None):
    if installdb == None:
        installdb = inary.db.installdb.InstallDB()
    G_f = PGraph(installdb)  # construct G_f
    for x in A:
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = installdb.get_package(x)
            for dep in pkg.runtimeDependencies():
                if dep.package in G_f.vertices():
                    G_f.add_dep(x, dep)
        B = Bp
    if ctx.get_option('debug'):
        import sys
        G_f.write_graphviz(sys.stdout)
    order = G_f.sort()

    return order
