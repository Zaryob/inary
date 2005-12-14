#! /usr/bin/python
# a simple tool to list stuff in source repository
# author: exa

import sys
import os
sys.path.insert(0, '.')

import pisi.context as ctx
#ctx.usemdom = True
import pisi
import pisi.api
import pisi.config
import pisi.specfile as specfile
import pisi.util
from pisi.graph import Digraph

options = pisi.config.Options()
if len(sys.argv) > 2:
    options.destdir=sys.argv[2]
else:
    options.destdir = '/'
pisi.api.init(database=False, options=options)
repo_uri = sys.argv[1]

specfiles = []

for root, dirs, files in os.walk(repo_uri):
    for fn in files:
        if fn == 'pspec.xml':
            #ctx.ui.info(_('Adding %s to package index') % fn)
            sf = specfile.SpecFile()
            sf.read(pisi.util.join_path(root, fn))
            sf.check()
            print 'read %s: %s' % (sf.source.name, sf.source.version)
            specfiles.append(sf)

def plan_build(specfiles):
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = Digraph()    
    pkgtosrc = {}
    for sf in specfiles:
        for pkg in sf.packages:
            pkgtosrc[str(pkg.name)] = str(sf.source.name) 
    
    for x in specfiles:
        #G_f.add_package(x)
        src = x.source
        print "adding vtx ", str(src.name)
        if not str(src.name) in G_f.vertices():
            G_f.add_vertex(str(src.name), (src.version, src.release))
        for builddep in src.buildDependencies:
            G_f.add_edge(str(src.name), str(builddep.package))
        for pkg in x.packages:
            for rtdep in pkg.packageDependencies:
                G_f.add_edge(str(src.name), pkgtosrc[rtdep.package])
    
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    return G_f, order

G_f, order = plan_build(specfiles)

print order 
pisi.api.finalize()
