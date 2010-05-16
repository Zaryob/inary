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

"""PiSi package relation graph that represents the state of packagedb"""

import graph

# Cache the results from packagedb queries in a graph

class PGraph(graph.Digraph):

    def __init__(self, packagedb):
        super(PGraph, self).__init__()
        self.packagedb = packagedb

    def add_package(self, pkg):
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
                      pkg1data, pkg2data )

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
                      pkg1data, pkg2data )

    def write_graphviz_vlabel(self, f, u):
        (v, r) = self.vertex_data(u)
        f.write('[ label = \"' + str(u) + '(' + str(v) + ',' + str(r) + ')\" ]')

