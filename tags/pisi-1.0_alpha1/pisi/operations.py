# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
#

"Package Operations: install/remove/upgrade"

import os

import pisi
import pisi.context as ctx
import pisi.util as util
import pisi.packagedb as packagedb
from pisi.uri import URI

# single package operations

def remove_single(package_name):
    """Remove a single package"""
    inst_packagedb = packagedb.inst_packagedb

    #TODO: check dependencies

    ctx.ui.info('Removing package %s' % package_name)
    if not ctx.installdb.is_installed(package_name):
        raise Exception('Trying to remove nonexistent package '
                        + package_name)
    if ctx.comard:
        ctx.comard.remove(package_name)
        ctx.comard.call("System.Package", "preremove")
    for fileinfo in ctx.installdb.files(package_name).list:
        fpath = os.path.join(ctx.config.destdir, fileinfo.path)
        # TODO: We have to store configuration files for futher
        # usage. Currently we'are doing it like rpm does, saving
        # with a prefix and leaving the user to edit it. In the future
        # we'll have a plan for these configuration files.
        if fileinfo.type == ctx.const.conf:
            if os.path.isfile(fpath):
                os.rename(fpath, fpath + ".pisi")
        else:
            # check if file is removed manually.
            # And we don't remove directories!
            # FIXME: should give a warning if it is...
            if os.path.isfile(fpath):
                os.unlink(fpath)


    ctx.installdb.remove(package_name)
    packagedb.remove_package(package_name)

def install_single(pkg, upgrade = False):
    """install a single package from URI or ID"""
    url = URI(pkg)
    # Check if we are dealing with a remote file or a real path of
    # package filename. Otherwise we'll try installing a package from
    # the package repository.
    if url.is_remote_file() or os.path.exists(url.uri):
        install_single_file(pkg, upgrade)
    else:
        install_single_name(pkg, upgrade)

# FIXME: Here and elsewhere pkg_location must be a URI
def install_single_file(pkg_location, upgrade = False):
    """install a package file"""
    from install import Installer
    Installer(pkg_location).install(not upgrade)

def install_single_name(name, upgrade = False):
    """install a single package from ID"""
    # find package in repository
    repo = packagedb.which_repo(name)
    if repo:
        repo = ctx.repodb.get_repo(repo)
        pkg = packagedb.get_package(name)

        # FIXME: let pkg.packageURI be stored as URI type rather than string
        pkg_uri = URI(pkg.packageURI)
        if pkg_uri.is_absolute_path():
            pkg_path = str(pkg.packageURI)
        else:
            pkg_path = os.path.join(os.path.dirname(repo.indexuri.get_uri()),
                                    str(pkg_uri.path()))

        ctx.ui.debug("Package URI: %s" % pkg_path)

        # Package will handle remote file for us!
        install_single_file(pkg_path, upgrade)
    else:
        ctx.ui.error("Package %s not found in any active repository." % pkg)

# deneme, don't remove ulan
class AtomicOperation(object):
    def __init__(self, package, ignore_dep = False):
        self.package = package
        self.ignore_dep = ignore_dep

    def run(self, package):
        "perform an atomic package operation"
        pass
