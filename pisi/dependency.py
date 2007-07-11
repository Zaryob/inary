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

"""dependency analyzer"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
import pisi.relation

""" Dependency relation """
class Dependency(pisi.relation.Relation):
    def __str__(self):
        s = self.package
        if self.versionFrom:
            s += _(" version >= ") + self.versionFrom
        if self.versionTo:
            s += _(" version <= ") + self.versionTo
        if self.version:
            s += _(" version ") + self.version
        if self.releaseFrom:
            s += _(" release >= ") + self.releaseFrom
        if self.releaseTo:
            s += _(" release <= ") + self.releaseTo
        if self.release:
            s += _(" release ") + self.release
        return s

def dict_satisfies_dep(dict, depinfo):
    """determine if a package in a dictionary satisfies given dependency spec"""
    pkg_name = depinfo.package
    if not dict.has_key(pkg_name):
        return False
    else:
        pkg = dict[pkg_name]
        (version, release) = (pkg.version, pkg.release)
        return depinfo.satisfies_relation(pkg_name, version, release)

def installed_satisfies_dep(depinfo):
    """determine if a package in *repository* satisfies given
dependency spec"""
    return pisi.relation.installed_package_satisfies(depinfo)

def repo_satisfies_dep(depinfo):
    """determine if a package in *repository* satisfies given
dependency spec"""
    pkg_name = depinfo.package
    if not ctx.packagedb.has_package(pkg_name):
        return False
    else:
        pkg = ctx.packagedb.get_package(pkg_name)
        (version, release) = (pkg.version, pkg.release)
        return depinfo.satisfies_relation(pkg_name, version, release)

def satisfies_dependencies(pkg, deps, sat = installed_satisfies_dep):
    for dep in deps:
        if not sat(dep):
            ctx.ui.error(_('%s dependency of package %s is not satisfied') %
                     (dep, pkg))
            return False
    return True

def satisfies_runtime_deps(pkg):
    deps = ctx.packagedb.get_package(pkg).runtimeDependencies()
    return satisfies_dependencies(pkg, deps)

def installable(pkg):
    """calculate if pkg name is installable currently
    which means it has to satisfy both install and runtime dependencies"""
    if not ctx.packagedb.has_package(pkg):
        ctx.ui.info(_("Package %s is not present in the package database") % pkg);
        return False
    elif satisfies_runtime_deps(pkg):
        return True
    else:
        return False
