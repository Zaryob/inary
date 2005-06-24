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
    print 'installdeps = ', deps
    return reduce(lambda x,y:x and y,
                  map(lambda x: satisfiesDep(pkg, x), deps),True)

def runtimeDeps(pkg):
    return packagedb.get_package(pkg).runtimeDeps

def satisfiesRuntimeDeps(pkg):
    deps = runtimeDeps(pkg)
    print 'runtimedeps = ', deps
    return reduce(lambda x,y:x and y,
                  map(lambda x: satisfiesDep(pkg, x), deps),True)

def installable(pkg):
    """calculate if pkg is installable currently 
    which means it has to satisfy both install and runtime dependencies"""
    if not packagedb.has_package(pkg):
        ui.info("package " + pkg + " is not present in the package database\n");
        return False
    elif not satisfiesRuntimeDeps(pkg) and satisfiesInstallDeps(pkg):
        ui.info("package " + pkg + " does not satisfy dependencies\n");
        return False
    else:
        return True

