# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# top level PISI interfaces
# a facade to the entire PISI system

import os
import sys
ver = sys.version_info
if ver[0] <= 2 and ver[1] < 4:
    from sets import Set as set

from config import config
from constants import const
from ui import ui
from purl import PUrl
import util, dependency, pgraph, operations, packagedb
from repodb import repodb
from installdb import installdb
from index import Index

def install(packages):
    """install a list of packages (either files/urls, or names)"""
    # determine if this is a list of files/urls or names
    try:
        if packages[0].endswith(const.package_prefix): # they all have to!
            install_pkg_files(packages)
        else:
            install_pkg_names(packages)
    except packagedb.PackageDBError, e:
        ui.error("PackageDBError: (%s)\n" % e)
        ui.error("Package is not installable. Its very likely a dependency problem.\n")
        

def install_pkg_files(packages):
    """install a number of pisi package files"""
    from package import Package

    for x in packages:
        if not x.endswith(const.package_prefix):
            ui.error('Mixing file names and package names not supported\n')
            return False

    # read the package information into memory first
    # regardless of which distribution they come from
    d_t = {}
    for x in packages:
        package = Package(x)
        package.read()
        d_t[package.metadata.package.name] = package.metadata

    # for this case, we have to determine the dependencies
    # that aren't already satisfied and try to install them 
    # from the repository
    dep_unsatis = []
    for name in d_t.keys():
        md = d_t[name]
        deps = md.package.runtimeDeps
        if not dependency.satisfiesDeps(md.package.name, deps):
            dep_unsatis += deps

    # now determine if these unsatisfied dependencies could
    # be satisfied by installing packages from the repo

    # if so, then invoke install_pkg_names
    if install_pkg_names([x.package for x in dep_unsatis]):
        for x in packages:
            operations.install_single_file(x)

def install_pkg_names(A):
    """This is the real thing. It installs packages from
    the repository, trying to perform a minimum number of
    installs"""

    if len(A)==0:
        return True
    
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph()               # construct G_f

    # find the "install closure" graph of G_f by package 
    # set A using packagedb
    print A
    for x in A:
        G_f.add_package(x)
    B = A
    #state = {}
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            print pkg
            for dep in pkg.runtimeDeps:
                print 'checking ', dep
                # we don't deal with satisfied dependencies
                if not dependency.satisfiesDep(x, dep):
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    G_f.write_graphviz(sys.stdout)
    l = G_f.topological_sort()
    l.reverse()
    print l
    for x in l:
        operations.install_single_name(x)
        
    return True                         # everything went OK :)

def remove(A):
    """remove set A of packages from system"""
    
    if len(A)==0:
        return True
    
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph()               # construct G_f

    # find the "install closure" graph of G_f by package 
    # set A using packagedb
    print A
    for x in A:
        G_f.add_package(x)
    B = A
    #state = {}
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            print 'processing', pkg.name
            rev_deps = packagedb.get_rev_deps(x)
            for (rev_dep, depinfo) in rev_deps:
                print 'checking ', rev_dep
                # we don't deal with unsatisfied dependencies
                if dependency.satisfiesDep(rev_dep, depinfo):
                    if not rev_dep in G_f.vertices():
                        Bp.add(rev_dep)
                        G_f.add_plain_dep(rev_dep, x)
        B = Bp
    G_f.write_graphviz(sys.stdout)
    l = G_f.topological_sort()
    print l
    for x in l:
        if installdb.is_installed(x):
            operations.remove_single(x)
        
    return True                         # everything went OK :)


def info(package_name):
    from package import Package

    package = Package(package_name)
    package.read()
    return package.metadata, package.files


def index(repo_dir = '.'):
    from index import Index

    ui.info('* Building index of PISI files under %s\n' % repo_dir)
    index = Index()
    index.index(repo_dir)
    index.write(const.pisi_index)
    ui.info('* Index file written\n')

class Repo:
    def __init__(self, indexuri):
        self.indexuri = indexuri

def add_repo(name, indexuri):
    repo = Repo(PUrl(indexuri))
    repodb.add_repo(name, repo)

def remove_repo(name):
    repodb.remove_repo(name)

def update_repo(repo):

    ui.info('* Updating repository: %s\n' % repo)
    index = Index()
    index.read(repodb.get_repo(repo).indexuri.getUri(), repo)
    index.update_db(repo)
    ui.info('* Package db updated.\n')


# build functions...
def prepare_for_build(pspecfile, authInfo=None):
    from build import PisiBuild

    url = PUrl(pspecfile)
    if url.isRemoteFile():
        from sourcefetcher import SourceFetcher
        fs = SourceFetcher(url, authInfo)
        url.uri = fs.fetch_all()

    pb = PisiBuild(url.uri)
    return pb

def build(pspecfile, authInfo=None):
    pb = prepare_for_build(pspecfile, authInfo)
    pb.build()


order = {"none": 0,
         "unpack": 1,
         "setupaction": 2,
         "buildaction": 3,
         "installaction": 4,
         "buildpackages": 5}

def __buildState_unpack(pb):
    # unpack is the first state to run.
    pb.fetchSourceArchive()
    pb.unpackSourceArchive()
    pb.applyPatches()

    pb.setState("unpack")

def __buildState_setupaction(pb, last):

    if order[last] < order["unpack"]:
        __buildState_unpack(pb)
    pb.runSetupAction()

    pb.setState("setupaction")

def __buildState_buildaction(pb, last):

    if order[last] < order["setupaction"]:
        __buildState_setupaction(pb, last)
    pb.runBuildAction()

    pb.setState("buildaction")

def __buildState_installaction(pb, last):
    
    if order[last] < order["buildaction"]:
        __buildState_buildaction(pb, last)
    pb.runInstallAction()

    pb.setState("installaction")

def __buildState_buildpackages(pb, last):

    if order[last] < order["installaction"]:
        __buildState_installaction(pb, last)
    pb.buildPackages()

    pb.setState("buildpackages")

def build_until(pspecfile, state, authInfo=None):
    pb = prepare_for_build(pspecfile, authInfo)
    pb.compileActionScript()
    
    last = pb.getState()
    ui.info("Last state was %s\n"%last)

    if not last: last = "none"

    if state == "unpack":
        __buildState_unpack(pb)
        return

    if state == "setupaction":
        __buildState_setupaction(pb, last)
        return
    
    if state == "buildaction":
        __buildState_buildaction(pb, last)
        return

    if state == "installaction":
        print "blibli"
        __buildState_installaction(pb, last)
        return

    __buildState_buildpackages(pb, last)
    



