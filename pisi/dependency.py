# dependency analyzer
# maintainer: eray and caglar

import installdb
import packagedb
from ui import ui
from version import Version

def satisfiesDep(pkg, depinfo):
    """determine if a package satisfies given dependency spec"""
    if not installdb.is_installed(depinfo.package):
        return False
    else:
        (version, release) = installdb.get_info(pkg)
        ret = True
        if depinfo.versionFrom:
            ret &= Version(version) >= Version(depinfo.versionFrom)
        if depinfo.versionTo:
            ret &= Version(version) <= Version(depinfo.versionTo)        
        return ret

def installDeps(pkg):
    return packagedb.get_package(pkg).installDeps

def satisfiesInstallDeps(pkg):
    deps = installDeps(pkg)
    return reduce(lambda x,y:x and y,
                  map(lambda x: satisfiesDep(pkg, x), deps))

def runtimeDeps(pkg):
    return packagedb.get_package(pkg).runtimeDeps

def satisfiesRuntimeDeps(pkg):
    deps = runtimeDeps(pkg)
    return reduce(lambda x,y:x and y,
                  map(lambda x: satisfiesDep(pkg, x), deps))

def installable(pkg):
    """calculate if pkg is installable currently 
    which means it has to satisfy both install and runtime dependencies"""
    if not packagedb.has_package(pkg):
        ui.info("package " + pkg + " not installable");
        return False
    else:
        return satisfiesRuntimeDeps(pkg) and satisfiesInstallDeps(pkg)
