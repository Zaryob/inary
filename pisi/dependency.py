# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# dependency analyzer

# Author:  Eray Ozkural <eray@uludag.org.tr>

from installdb import installdb
import packagedb
from ui import ui
from version import Version

def satisfiesDep(pkg_name, depinfo):
    """determine if package satisfies given dependency spec in installdb"""
    if not installdb.is_installed(depinfo.package):
        return False
    else:
        pkg = packagedb.get_package(pkg_name)
        (version, release) = (pkg.version, pkg.release)
        return depinfo.satisfies(pkg_name, version, release)

def satisfiesDeps(pkg, deps):
    for dep in deps:
        if not satisfiesDep(pkg, dep):
            ui.error('Package %s does not satisfy dependency %s\n' %
                     (pkg,dep))
            return False
    return True

def runtimeDeps(pkg):
    return packagedb.get_package(pkg).runtimeDeps

def satisfiesRuntimeDeps(pkg):
    deps = runtimeDeps(pkg)
    return satisfiesDeps(pkg, deps)

def installable(pkg):
    """calculate if pkg is installable currently 
    which means it has to satisfy both install and runtime dependencies"""
    if not packagedb.has_package(pkg):
        ui.info("package " + pkg + " is not present in the package database\n");
        return False
    elif satisfiesRuntimeDeps(pkg):
        return True
    else:
        #ui.info("package " + pkg + " does not satisfy dependencies\n");
        return False

