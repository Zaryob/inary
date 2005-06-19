# dependency analyzer
# maintainer: eray and caglar

import installdb
import packagedb
import ui

# FIXME: this is supposed to handle all those attributes
def satisfiesDep(pkg, depinfo):
    """determine if a package satisfies given dependency spec"""
    if not installdb.is_installed(depinfo.package):
        return False
    else:
        (version, release) = installdb.get_info(pkg)
        # FIXME: specific processing for attributes
        return True

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
    if not packagedb.has_key(pkgname):
        ui.info("package " + pkgname + " not installable");
        return False
    else:
        return satisfiesRuntimeDeps(pkg) and satisfiesInstallDeps(pkg)

