# PISI package relation graph that represents the state of packagedb

import packagedb
from sourcedb import sourcedb
from graph import *

# Cache the results from packagedb queries in a graph

class PGraph(digraph):
    
    def __init__(self):
        super(PGraph, self).__init__()

    def add_dep(self, pkg, depinfo):
        pkg1data = None
        if not pkg in self.vertices():
            pkg1 = packagedb.get_package(pkg)
        pkg2data = None
        if not pkg in self.vertices():
            pkg2 = packagedb.get_package(depinfo.package)

        self.add_edge(pkg, depinfo.package, ('d', depinfo),
                      (pkg1.version, pkg1.release),
                      (pkg2.version, pkg2.release) )

    def add_conflict(self, pkg, conflinfo):
        pkg1data = None
        if not pkg in self.vertices():
            pkg1 = packagedb.get_package(pkg)
        pkg2data = None
        if not pkg in self.vertices():
            pkg2 = packagedb.get_package(depinfo.package)

        self.add_biedge(pkg, conflinfo.package, ('c', conflinfo)
                        (pkg1.version, pkg1.release),
                        (pkg2.version, pkg2.release) )


    def write_graphviz_vlabel(self, f, u):
        (v, r) = self.vertex_data(u)
        f.write('[ ' + str(u) + '(' + str(v) + ',' + str(r) + ') ]')

