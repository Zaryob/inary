# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
# Author:  Eray Ozkural <eray@uludag.org.tr>

"Package Operations: install/remove/upgrade"

import os
import sys
ver = sys.version_info
if ver[0] <= 2 and ver[1] < 4:
    from sets import Set as set

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.context as ctx
from pisi.uri import URI
import pisi.util as util
import pisi.dependency as dependency
import pisi.pgraph as pgraph
import pisi.packagedb as packagedb
import pisi.repodb
import pisi.installdb
from pisi.index import Index
import pisi.cli
import pisi.atomicoperations as atomicoperations

class Error(pisi.Error):
    pass

# high level operations
def install(packages, reinstall = False):
    """install a list of packages (either files/urls, or names)"""

    # FIXME: this function name "install" makes impossible to import
    # and use install module directly.
    from pisi.atomicoperations import Error as InstallError

    # determine if this is a list of files/urls or names
    if packages[0].endswith(ctx.const.package_suffix): # they all have to!
        return install_pkg_files(packages)
    else:
        return install_pkg_names(packages, reinstall)

def install_pkg_files(package_URIs):
    """install a number of pisi package files"""
    from package import Package

    ctx.ui.debug('A = %s' % str(package_URIs))

    for x in package_URIs:
        if not x.endswith(ctx.const.package_suffix):
            raise Error(_('Mixing file names and package names not supported yet.'))

    if ctx.config.get_option('ignore_dependency'):
        # simple code path then
        for x in package_URIs:
            atomicoperations.install_single_file(x)
        return # short circuit
            
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
        # is dependency satisfied among available packages
        # or packages to be installed?
        return dependency.installed_satisfies_dep(dep) \
               or dependency.dict_satisfies_dep(d_t, dep)
            
    # for this case, we have to determine the dependencies
    # that aren't already satisfied and try to install them 
    # from the repository
    dep_unsatis = []
    for name in d_t.keys():
        pkg = d_t[name]
        deps = pkg.runtimeDependencies()
        for dep in deps:
            if not satisfiesDep(dep):
                dep_unsatis.append(dep)

    # now determine if these unsatisfied dependencies could
    # be satisfied by installing packages from the repo

    # if so, then invoke install_pkg_names
    extra_packages = [x.package for x in dep_unsatis]
    if extra_packages:
        ctx.ui.info(_("""The following packages will be installed
in the respective order to satisfy extra dependencies:
""") + util.strlist(extra_packages))
        if not ctx.ui.confirm(_('Do you want to continue?')):
            raise Error(_('External dependencies not satisfied'))
        install_pkg_names(extra_packages)

    class PackageDB:
        def get_package(self, key):
            return d_t[str(key)]
    
    packagedb = PackageDB()
   
    A = d_t.keys()
   
    if len(A)==0:
        ctx.ui.info(_('No packages to install.'))
        return
    
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(packagedb)               # construct G_f

    # find the "install closure" graph of G_f by package 
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            for dep in pkg.runtimeDependencies():
                if dependency.dict_satisfies_dep(d_t, dep):
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    ctx.ui.info(_('Installation order: ') + util.strlist(order) )

    if ctx.get_option('dry_run'):
        return

    for x in order:
        atomicoperations.install_single_file(dfn[x])

def check_conflicts(order):
    """check if upgrading to the latest versions will cause havoc
    done in a simple minded way without regard for dependencies of
    conflicts, etc."""
    B_0 = B = set(order)
    C = set()
    # calculate conflict closure
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x) # get latest version!
            #TODO: read conflicts from a conflicts db...
            for conflict in pkg.conflicts:
                if ctx.installdb.is_installed(self.pkginfo):
                    Bp.add(conflict)
                    C.add(conflict)
        B = Bp
    if B_0.intersection(C):
        raise Error(_("Selected packages %s and %s are in conflict.") % (x, pkg))
    if C:
        if not ctx.ui.confirm(_('Remove the following conflicting packages?')):
            #raise Error(_("Package %s conflicts installed package %s") % (x, pkg))
            raise Error(_("Conflicts remain"))

def expand_components(A):
    Ap = set()
    for x in A:
        if ctx.componentdb.has_component(x):
            Ap = Ap.union(ctx.componentdb.get_component(x).packages)
        else:
            Ap.add(x)
    return Ap

def install_pkg_names(A, reinstall = False):
    """This is the real thing. It installs packages from
    the repository, trying to perform a minimum number of
    installs"""

    # A was a list, remove duplicates and expand components
    A_0 = A = expand_components(set(A))
    ctx.ui.debug('A = %s' % str(A))

    # filter packages that are already installed
    if not reinstall:
        Ap = set(filter(lambda x: not ctx.installdb.is_installed(x), A))
        d = A - Ap
        if len(d) > 0:
            ctx.ui.warning(_('Not re-installing the following packages: ') +
                           util.strlist(d))
            A = Ap

    if len(A)==0:
        ctx.ui.info(_('No packages to install.'))
        return
        
    if not ctx.config.get_option('ignore_dependency'):
        G_f, order = plan_install_pkg_names(A)
    else:
        G_f = None
        order = A

    ctx.ui.info(_("""The following minimal list of packages will be installed
in the respective order to satisfy dependencies:
""") + util.strlist(order))

    if ctx.get_option('dry_run'):
        return

    if len(order) > len(A_0):
        if not ctx.ui.confirm(_('There are extra packages due to dependencies. Do you want to continue?')):
            return False
    for x in order:
        atomicoperations.install_single_name(x)

def plan_install_pkg_names(A):
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(packagedb)               # construct G_f

    # find the "install closure" graph of G_f by package 
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            for dep in pkg.runtimeDependencies():
                ctx.ui.debug('checking %s' % str(dep))
                # we don't deal with already *satisfied* dependencies
                if not dependency.installed_satisfies_dep(dep):
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    check_conflicts(order)
    return G_f, order

def upgrade(A):
    upgrade_pkg_names(A)

def upgrade_pkg_names(A = []):
    """Re-installs packages from the repository, trying to perform
    a maximum number of upgrades."""
    
    ignore_build = ctx.config.options and ctx.config.options.ignore_build_no

    if not A:
        # if A is empty, then upgrade all packages
        A = ctx.installdb.list_installed()

    # filter packages that are not upgradable
    A_0 = A = expand_components(set(A))
    Ap = []
    for x in A:
        if x.endswith(ctx.const.package_suffix):
            ctx.ui.debug(_("Warning: package *name* ends with '.pisi'"))
        if not ctx.installdb.is_installed(x):
            ctx.ui.info(_('Package %s is not installed.') % x)
            continue
        (version, release, build) = ctx.installdb.get_version(x)
        pkg = packagedb.get_package(x)

        # First check version. If they are same, check release. Again
        # if releases are same and checking buildno is premitted,
        # check build number.
        if version < pkg.version:
            Ap.append(x)
        elif version == pkg.version:
            if release < pkg.release:
                Ap.append(x)
            if release == pkg.release and build and not ignore_build:
                if build < pkg.build:
                    Ap.append(x)
        else:
            #ctx.ui.info('Package %s cannot be upgraded. ' % x)
            ctx.ui.info(_('Package %s is already at its latest \
version %s, release %s, build %s.')
                    % (x, pkg.version, pkg.release, pkg.build))
    A = set(Ap)

    if len(A)==0:
        ctx.ui.info(_('No packages to upgrade.'))
        return True

    ctx.ui.debug('A = %s' % str(A))
    
    if not ctx.config.get_option('ignore_dependency'):
        G_f, order = plan_upgrade(A)
    else:
        G_f = None
        order = A

    ctx.ui.info(_("""The following packages will be upgraded:\n""") +
                util.strlist(order))

    if ctx.get_option('dry_run'):
        return

    if len(order) > len(A_0):
        if not ctx.ui.confirm(_('There are extra packages due to dependencies. Do you want to continue?')):
            return False

    install_ops = [atomicoperations.Install.from_name(x) for x in order]
    
    for install in install_ops:
        install.install(True)

def plan_upgrade(A):
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(packagedb)               # construct G_f

    # find the "install closure" graph of G_f by package 
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    
    def upgradable(dep):
        #pre dep.package is installed
        (v,r,b) = ctx.installdb.get_version(dep.package)
        rep_pkg = packagedb.get_package(dep.package)
        (vp,rp,bp) = (rep_pkg.version, rep_pkg.release, 
                      rep_pkg.build)
        if ignore_build or (not b) or (not bp):
            # if we can't look at build
            if r >= rp:     # installed already new
                return False
        elif b and bp and b >= bp:
            return False
        return True

    # TODO: conflicts

    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            for dep in pkg.runtimeDependencies():
                # add packages that can be upgraded
                if dependency.repo_satisfies_dep(dep):
                    #TODO: distinguish must upgrade and upgradable
                    if ctx.installdb.is_installed(dep.package):
                        if not ctx.get_option('eager'):
                            if dependency.installed_satisfies_dep(dep):
                                continue
                        else:
                            if not upgradable(dep):
                                continue
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
                else:
                    raise Error(_("Reverse dependency %s cannot be satisfied") % rev_dep)
        B = Bp
    # now, search reverse dependencies to see if anything
    # should be upgraded
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            rev_deps = packagedb.get_rev_deps(x)
            for (rev_dep, depinfo) in rev_deps:
                if not ctx.get_option('eager'):
                    # add unsatisfied reverse dependencies
                    if packagedb.has_package(rev_dep) and \
                       (not dependency.installed_satisfies_dep(depinfo)):
                        if not dependency.repo_satisfies_dep(dep):
                            raise Error(_("Reverse dependency %s cannot be satisfied") % rev_dep)
                        if not rev_dep in G_f.vertices():
                            Bp.add(rev_dep)
                            G_f.add_plain_dep(rev_dep, x)
                else:
                    if not rev_dep in G_f.vertices():
                        Bp.add(rev_dep)
                        G_f.add_plain_dep(rev_dep, x)
        B = Bp

    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    check_conflicts(order)
    return G_f, order

def remove(A):
    """remove set A of packages from system (A is a list of package names)"""
    
    # filter packages that are not installed
    A_0 = A = expand_components(set(A))

    if not ctx.get_option('bypass_safety'):
        if ctx.componentdb.has_component('system.base'):
            refused = A.intersection(set(ctx.componentdb.get_component('system.base').packages))
            if refused:
                ctx.ui.warning(_('Safety switch: cannot remove the following packages in system.base: ') +
                               util.strlist(refused))
                A = A - set(ctx.componentdb.get_component('system.base').packages)
        else:
            ctx.ui.warning(_('Safety switch: the component system.base cannot be found'))

    Ap = []
    for x in A:
        if ctx.installdb.is_installed(x):
            Ap.append(x)
        else:
            ctx.ui.info(_('Package %s does not exist. Cannot remove.') % x)
    A = set(Ap)

    if len(A)==0:
        ctx.ui.info(_('No packages to remove.'))
        return

    if not ctx.config.get_option('ignore_dependency'):
        G_f, order = plan_remove(A)
    else:
        G_f = None
        order = A

    ctx.ui.info(_("""The following minimal list of packages will be removed
in the respective order to satisfy dependencies:
""") + util.strlist(order))
    if len(order) > len(A_0):
        if not ctx.ui.confirm(_('Do you want to continue?')):
            ctx.ui.warning(_('Package removal declined'))
            return False
    
    if ctx.get_option('dry_run'):
        return
    
    for x in order:
        if ctx.installdb.is_installed(x):
            atomicoperations.remove_single(x)
        else:
            ctx.ui.info(_('Package %s is not installed. Cannot remove.') % x)


def plan_remove(A):
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph(packagedb)               # construct G_f

    # find the (install closure) graph of G_f by package 
    # set A using packagedb
    for x in A:
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            rev_deps = packagedb.get_rev_deps(x)
            for (rev_dep, depinfo) in rev_deps:
                # we don't deal with unsatisfied dependencies
                if packagedb.has_package(rev_dep) and \
                   dependency.installed_satisfies_dep(depinfo):
                    if not rev_dep in G_f.vertices():
                        Bp.add(rev_dep)
                        G_f.add_plain_dep(rev_dep, x)
        B = Bp
    if ctx.config.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    return G_f, order
