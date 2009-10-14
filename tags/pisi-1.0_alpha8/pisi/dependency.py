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

"""dependency analyzer"""

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

#import pisi.db as db
import pisi.context as ctx
import pisi.packagedb as packagedb
from pisi.version import Version
from pisi.xmlext import *
from pisi.xmlfile import XmlFile
from pisi.util import Checks

class DepInfo:
    def __init__(self, node = None):
        if node:
            self.package = getNodeText(node).strip()
            self.versionFrom = getNodeAttribute(node, "versionFrom")
            self.versionTo = getNodeAttribute(node, "versionTo")
            self.releaseFrom = getNodeAttribute(node, "releaseFrom")
            self.releaseTo = getNodeAttribute(node, "releaseTo")
        else:
            self.versionFrom = self.versionTo = None
            self.releaseFrom = self.releaseTo = None

    def elt(self, xml):
        node = xml.newNode("Dependency")
        xml.addText(node, self.package)
        if self.versionFrom:
            node.setAttribute("versionFrom", self.versionFrom)
        if self.versionTo:
            node.setAttribute("versionTo", self.versionTo)
        if self.releaseFrom:
            node.setAttribute("releaseFrom", self.versionFrom)
        if self.releaseTo:
            node.setAttribute("releaseTo", self.versionTo)
        return node

    def has_errors(self):
        if not self.package:
            return [ _("Dependency should have a package string") ]
        return []

    def satisfies(self, pkg_name, version, release):
        """determine if a package ver. satisfies given dependency spec"""
        ret = True
        v = Version(version)
        if self.versionFrom:
            ret &= v >= Version(self.versionFrom)
        if self.versionTo:
            ret &= v <= Version(self.versionTo)        
        if self.releaseFrom:
            ret &= v <= Version(self.releaseFrom)        
        if self.releaseTo:
            ret &= v <= Version(self.releaseTo)       
        return ret
        
    def __str__(self):
        s = self.package
        if self.versionFrom:
            s += 'ver >= ' + self.versionFrom
        if self.versionTo:
            s += 'ver <= ' + self.versionTo
        if self.releaseFrom:
            s += 'rel >= ' + self.releaseFrom
        if self.releaseTo:
            s += 'rel <= ' + self.releaseTo
        return s

def dict_satisfies_dep(dict, depinfo):
    """determine if a package in a dictionary satisfies given dependency spec"""
    pkg_name = depinfo.package
    if not dict.has_key(pkg_name):
        return False
    else:
        pkg = dict[pkg_name]
        (version, release) = (pkg.version, pkg.release)
        return depinfo.satisfies(pkg_name, version, release)

def installed_satisfies_dep(depinfo):
    """determine if a package in *repository* satisfies given
dependency spec"""
    pkg_name = depinfo.package
    if not ctx.installdb.is_installed(pkg_name):
        return False
    else:
        pkg = packagedb.inst_packagedb.get_package(pkg_name)
        (version, release) = (pkg.version, pkg.release)
        return depinfo.satisfies(pkg_name, version, release)

def repo_satisfies_dep(depinfo):
    """determine if a package in *repository* satisfies given
dependency spec"""
    pkg_name = depinfo.package
    if not packagedb.has_package(pkg_name):
        return False
    else:
        pkg = packagedb.get_package(pkg_name)
        (version, release) = (pkg.version, pkg.release)
        return depinfo.satisfies(pkg_name, version, release)

def satisfies_dependencies(pkg, deps, sat = installed_satisfies_dep):
    for dep in deps:
        if not sat(dep):
            ctx.ui.error(_('Package %s does not satisfy dependency %s') %
                     (pkg,dep))
            return False
    return True

def satisfies_runtime_deps(pkg):
    deps = packagedb.get_package(pkg).runtimeDeps
    return satisfies_dependencies(pkg, deps)

def installable(pkg):
    """calculate if pkg name is installable currently 
    which means it has to satisfy both install and runtime dependencies"""
    if not packagedb.has_package(pkg):
        ctx.ui.info(_("Package %s is not present in the package database") % pkg);
        return False
    elif satisfies_runtime_deps(pkg):
        return True
    else:
        return False

