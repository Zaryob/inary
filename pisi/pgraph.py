# PISI package relation graph that represents the state of packagedb

import packagedb
from sourcedb import sourcedb
from graph import *

# Cache the results from packagedb queries in a graph

class PGraph(digraph):
    
    def __init__(self):
        super(PGraph, self).__init__()

    def add_package(self, pkg):
        pkg1 = packagedb.get_package(pkg)
        self.add_vertex(str(pkg), (pkg1.version, pkg1.release))

    def add_dep(self, pkg, depinfo):
        pkg1data = None
        if not pkg in self.vertices():
            pkg1 = packagedb.get_package(pkg)
            pkg1data = (pkg1.version, pkg1.release) 
        pkg2data = None
        if not depinfo.package in self.vertices():
            pkg2 = packagedb.get_package(depinfo.package)
            pkg2data = (pkg2.version, pkg2.release)
        self.add_edge(str(pkg), str(depinfo.package), ('d', depinfo),
                      pkg1data, pkg2data )

    def add_rev_dep(self, depinfo, pkg):
        pkg1data = None
        if not pkg in self.vertices():
            pkg1 = packagedb.get_package(depinfo.package)
            pkg1data = (pkg1.version, pkg1.release)
        pkg2data = None
        if not depinfo.package in self.vertices():
            pkg2 = packagedb.get_package(pkg)
            pkg2data = (pkg2.version, pkg2.release) 
        self.add_edge(str(depinfo.package), str(pkg), ('d', depinfo),
                      pkg1data, pkg2data )

    def add_conflict(self, pkg, conflinfo):
        pkg1data = None
        if not pkg in self.vertices():
            pkg1 = packagedb.get_package(pkg)
            pkg1data = (pkg1.version, pkg1.release) 
        pkg2data = None
        if not pkg in self.vertices():
            pkg2 = packagedb.get_package(depinfo.package)
            pkg2data = (pkg2.version, pkg2.release)

        self.add_biedge(str(pkg), str(conflinfo.package), ('c', conflinfo)
                        , pkg1data, pkg2data )

    def write_graphviz_vlabel(self, f, u):
        (v, r) = self.vertex_data(u)
        f.write('[ ' + str(u) + '(' + str(v) + ',' + str(r) + ') ]')

