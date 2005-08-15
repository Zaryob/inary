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

from pisi.config import config
from pisi.constants import const
from pisi.ui import ui
from pisi.uri import URI
import pisi.util as util
import pisi.dependency as dependency
import pisi.pgraph as pgraph
import pisi.operations as operations
import pisi.packagedb as packagedb
from pisi.repodb import repodb
from pisi.installdb import installdb
from pisi.index import Index

class Error:
    pass

def install(packages):
    """install a list of packages (either files/urls, or names)"""

    # FIXME: this function name "install" makes impossible to import
    # and use install module directly.
    from install import InstallError

    try:
        # determine if this is a list of files/urls or names
        if packages[0].endswith(const.package_prefix): # they all have to!
            install_pkg_files(packages)
        else:
            install_pkg_names(packages)

    except InstallError, e:
        ui.error("%s\n" % e)

    except packagedb.PackageDBError, e:
        ui.error("PackageDBError: (%s)\n" % e)
        ui.error("Package is not installable.\n")

    #except Exception, e:
    #    print e
    #    ui.error("Error: %s\n" % e)


def install_pkg_files(package_URIs):
    """install a number of pisi package files"""
    from package import Package

    ui.debug('A = %s\n' % str(package_URIs))

    for x in package_URIs:
        if not x.endswith(const.package_prefix):
            ui.error('Mixing file names and package names not supported YET.\n')
            return False

    # read the package information into memory first
    # regardless of which distribution they come from
    d_t = {}
    dfn = {}
    for x in package_URIs:
        package = Package(x)
        package.read()
        name = str(package.metadata.package.name)
        d_t[name] = package.metadata.package
        dfn[name] = x

    def satisfiesDep(dep):
        return dependency.installed_satisfies_dep(dep) \
               or dependency.dict_satisfies_dep(d_t, dep)
            
    # for this case, we have to determine the dependencies
    # that aren't already satisfied and try to install them 
    # from the repository
    dep_unsatis = []
    for name in d_t.keys():
        pkg = d_t[name]
        deps = pkg.runtimeDeps
        for dep in deps:
            if not satisfiesDep(dep):
                dep_unsatis.append(dep)

    # now determine if these unsatisfied dependencies could
    # be satisfied by installing packages from the repo

    # if so, then invoke install_pkg_names
    extra_packages = [x.package for x in dep_unsatis]
    if (extra_packages and install_pkg_names(extra_packages)) or \
           (not extra_packages):
    
        class PackageDB:
            def __init__(self):
                self.d = d_t
            
            def get_package(self, key):
                return d_t[str(key)]
        
        packagedb = PackageDB()
       
        A = d_t.keys()
       
        if len(A)==0:
            ui.info('No packages to install.\n')
            return True
        
        # try to construct a pisi graph of packages to
        # install / reinstall
    
        G_f = pgraph.PGraph(packagedb)               # construct G_f
    
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
                    if dependency.dict_satisfies_dep(d_t, dep):
                        if not dep.package in G_f.vertices():
                            Bp.add(str(dep.package))
                        G_f.add_dep(x, dep)
            B = Bp
        G_f.write_graphviz(sys.stdout)
        order = G_f.topological_sort()
        order.reverse()
        print order

        for x in order:
            operations.install_single_file(dfn[x])
    else:
        raise Error('External dependencies not satisfied')

    return True # everything went OK.

def install_pkg_names(A):
    """This is the real thing. It installs packages from
    the repository, trying to perform a minimum number of
    installs"""

    ui.debug('A = %s\n' % str(A))

    if len(A)==0:
        ui.info('No packages to install.\n')
        return True
    
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(packagedb)               # construct G_f

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
                # we don't deal with already *satisfied* dependencies
                if not dependency.installed_satisfies_dep(dep):
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    print order
    for x in order:
        operations.install_single_name(x)
        
    return True                         # everything went OK :)


def upgrade(A):
    upgrade_pkg_names(A)


def upgrade_pkg_names(A):
    """Re-installs packages from the repository, trying to perform
    a maximum number of upgrades."""

    # filter packages that are not installed
    Ap = []
    for x in A:
        if not installdb.is_installed(x):
            ui.info('Package %s is not installed.\n' % x)
            continue
        (version, release, build) = installdb.get_version(x)
        pkg = packagedb.get_package(x)
        if (config.options and config.options.ignore_build_no) or (not build):
            if release < pkg.release:
                Ap.append(x)
        elif build < pkg.build:
                Ap.append(x)
        else:
            #ui.info('Package %s cannot be upgraded. ' % x)
            ui.info('Package %s is already at its latest version %s,\
 release %s, build %s.\n'
                    % (x, pkg.version, pkg.release, pkg.build))
    A = Ap

    if len(A)==0:
        ui.info('No packages to upgrade.\n')
        return True

    ui.debug('A = %s\n' % str(A))
    
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(packagedb)               # construct G_f

    # find the "install closure" graph of G_f by package 
    # set A using packagedb
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
                # add packages that can be upgraded
                if dependency.repo_satisfies_dep(dep):
                    if installdb.is_installed(dep.package):
                        (v,r,b) = installdb.get_version(dep.package)
                        rep_pkg = packagedb.get_package(dep.package)
                        (vp,rp,bp) = (rep_pkg.version, rep_pkg.release, 
                                      rep_pkg.build)
                        if r >= rp:     # installed already older
                            continue
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    print order
    for x in order:
        operations.install_single_name(x, True)
        
    return True                         # everything went OK :)

def remove(A):
    """remove set A of packages from system (A is a list of package names)"""
    
    # filter packages that are not installed
    Ap = []
    for x in A:
        if installdb.is_installed(x):
            Ap.append(x)
        else:
            ui.info('Package %s does not exist. Cannot remove.\n' % x)
    A = Ap

    if len(A)==0:
        ui.info('No packages to remove.\n')
        return True
        
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(packagedb)               # construct G_f

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
                if dependency.installed_satisfies_dep(depinfo):
                    if not rev_dep in G_f.vertices():
                        Bp.add(rev_dep)
                        G_f.add_plain_dep(rev_dep, x)
        B = Bp
    G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    print order
    for x in order:
        if installdb.is_installed(x):
            operations.remove_single(x)
        else:
            ui.info('Package %s is not installed. Cannot remove.\n' % x)
        
    return True                         # everything went OK :)

def configure_pending():
    # TODO: not coded yet
    # start with pending packages
    # configure them in reverse topological order of configuration dependency
    pass

def info(package_name):
    from package import Package

    package = Package(package_name)
    package.read()
    return package.metadata, package.files


def index(repo_dir = '.'):

    ui.info('* Building index of PISI files under %s\n' % repo_dir)
    index = Index()
    index.index(repo_dir)
    index.write(const.pisi_index)
    ui.info('* Index file written\n')

class Repo:
    def __init__(self, indexuri):
        self.indexuri = indexuri

def add_repo(name, indexuri):
    repo = Repo(URI(indexuri))
    repodb.add_repo(name, repo)

def remove_repo(name):
    if repodb.has_repo(name):
        repodb.remove_repo(name)
    else:
        ui.error('* Repository %s does not exist. Cannot remove.\n'
                 % name)

def update_repo(repo):

    ui.info('* Updating repository: %s\n' % repo)
    index = Index()
    index.read(repodb.get_repo(repo).indexuri.get_uri(), repo)
    index.update_db(repo)
    ui.info('* Package database updated.\n')


# build functions...
def prepare_for_build(pspecfile, authInfo=None):

    # FIXME: there is a function named "build" in this module which
    # makes it impossible to use build module directly.
    from build import PisiBuild

    url = URI(pspecfile)
    if url.is_remote_file():
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
    pb.fetch_source_archive()
    pb.unpack_source_archive()
    pb.apply_patches()

def __buildState_setupaction(pb, last):

    if order[last] < order["unpack"]:
        __buildState_unpack(pb)
    pb.run_setup_action()

def __buildState_buildaction(pb, last):

    if order[last] < order["setupaction"]:
        __buildState_setupaction(pb, last)
    pb.run_build_action()

def __buildState_installaction(pb, last):
    
    if order[last] < order["buildaction"]:
        __buildState_buildaction(pb, last)
    pb.run_install_action()

def __buildState_buildpackages(pb, last):

    if order[last] < order["installaction"]:
        __buildState_installaction(pb, last)
    pb.build_packages()

def build_until(pspecfile, state, authInfo=None):
    pb = prepare_for_build(pspecfile, authInfo)
    pb.compile_action_script()
    
    last = pb.get_state()
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
        __buildState_installaction(pb, last)
        return

    __buildState_buildpackages(pb, last)
