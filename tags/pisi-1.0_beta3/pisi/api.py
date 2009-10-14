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
# Authors:  Eray Ozkural <eray@uludag.org.tr>
#           Baris Metin <baris@uludag.org.tr>

"""Top level PISI interfaces. a facade to the entire PISI system"""

import os
import sys
from os.path import exists

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
import pisi.operations as operations
import pisi.packagedb as packagedb
import pisi.repodb
import pisi.installdb
import pisi.sourcedb
import pisi.component as component
from pisi.index import Index
import pisi.cli
from pisi.operations import install, remove, upgrade
from pisi.build import build, build_until
from pisi.atomicoperations import resurrect_package
from pisi.metadata import MetaData
from pisi.files import Files

class Error(pisi.Error):
    pass

def init(database = True, options = None, ui = None, comar = True):
    """Initialize PiSi subsystem"""

    import pisi.config
    ctx.config = pisi.config.Config(options)

    # TODO: this is definitely not dynamic beyond this point!
    ctx.comar = comar and not ctx.config.get_option('ignore_comar')

    if ui is None:
        if options:
            pisi.context.ui = pisi.cli.CLI(options.debug)
        else:
            pisi.context.ui = pisi.cli.CLI()
    else:
        pisi.context.ui = ui

    # initialize repository databases
    if database:
        ctx.repodb = pisi.repodb.init()
        ctx.installdb = pisi.installdb.init()
        ctx.filesdb = pisi.files.FilesDB()
        ctx.componentdb = pisi.component.ComponentDB()
        packagedb.init_db()
        pisi.sourcedb.init()
    else:
        ctx.repodb = None
        ctx.installdb = None
        ctx.filesdb = None
        ctx.componentdb = None
    ctx.ui.debug('PISI API initialized')
    ctx.initialized = True

def finalize():
    if ctx.initialized:
        pisi.repodb.finalize()
        pisi.installdb.finalize()
        if ctx.filesdb != None:
            ctx.filesdb.close()
        if ctx.componentdb != None:
            ctx.componentdb.close()
        packagedb.finalize_db()
        pisi.sourcedb.finalize()
        ctx.ui.debug('PISI API finalized')
        ctx.ui.close()
        ctx.initialized = False

def list_upgradable():
    ignore_build = ctx.config.options and ctx.config.options.ignore_build_no

    A = ctx.installdb.list_installed()
    # filter packages that are not upgradable
    Ap = []
    for x in A:
        if not ctx.installdb.is_installed(x):
            continue
        (version, release, build) = ctx.installdb.get_version(x)
        pkg = packagedb.get_package(x)
        if ignore_build or (not build):
            if release < pkg.release:
                Ap.append(x)
        elif build < pkg.build:
                Ap.append(x)
        else:
            pass
            #ctx.ui.info('Package %s cannot be upgraded. ' % x)
    return Ap


def package_graph(A, ignore_installed = False):
    """Construct a package relations graph, containing
    all dependencies of packages A, if ignore_installed
    option is True, then only uninstalled deps will
    be added."""

    ctx.ui.debug('A = %s' % str(A))
  
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
            #print pkg
            for dep in pkg.runtimeDependencies():
                if ignore_installed:
                    if dependency.installed_satisfies_dep(dep):
                        continue
                if not dep.package in G_f.vertices():
                    Bp.add(str(dep.package))
                G_f.add_dep(x, dep)
        B = Bp
    return G_f

def configure_pending():
    # start with pending packages
    # configure them in reverse topological order of dependency
    A = ctx.installdb.list_pending()
    G_f = pgraph.PGraph(packagedb)               # construct G_f
    for x in A.keys():
        G_f.add_package(x)
    B = A
    while len(B) > 0:
        Bp = set()
        for x in B.keys():
            pkg = packagedb.get_package(x)
            for dep in pkg.runtimeDependencies():
                if dep.package in G_f.vertices():
                    G_f.add_dep(x, dep)
        B = Bp
    if ctx.get_option('debug'):
        G_f.write_graphviz(sys.stdout)
    order = G_f.topological_sort()
    order.reverse()
    try:
        import pisi.comariface as comariface
        for x in order:
            pkginfo = A[x]
            pkgname = util.package_name(x, pkginfo.version,
                                        pkginfo.release,
                                        pkginfo.build,
                                        False)
            pkg_path = util.join_path(ctx.config.lib_dir(),
                                           pkgname)
            m = MetaData()
            metadata_path = util.join_path(pkg_path, ctx.const.metadata_xml)
            m.read(metadata_path)
            for pcomar in m.package.providesComar:
                scriptPath = util.join_path(pkg_path,
                                            ctx.const.comar_dir,
                                            pcomar.script)
                comariface.register(pcomar, x, scriptPath)
                comariface.run_postinstall(x)
            ctx.installdb.clear_pending(x)
    except ImportError:
        raise Error(_("COMAR: comard not fully installed"))

def info(package):
    if package.endswith(ctx.const.package_suffix):
        return info_file(package)
    else:
        return info_name(package)
    
def info_file(package_fn):
    from package import Package

    if not os.path.exists(package_fn):
        raise Error (_('File %s not found') % package_fn)

    package = Package(package_fn)
    package.read()
    return package.metadata, package.files

def info_name(package_name):
    """fetch package information for a package"""
    if packagedb.has_package(package_name):
        package = packagedb.get_package(package_name)
        from pisi.metadata import MetaData
        metadata = MetaData()
        metadata.package = package
        #FIXME: get it from sourcedb
        metadata.source = None
        #TODO: fetch the files from server if possible
        if ctx.installdb.is_installed(package.name):
            files = ctx.installdb.files(package.name)
        else:
            files = None
        return metadata, files
    else:
        raise Error(_('Package %s not found') % package_name)

def index(dirs, output = 'pisi-index.xml'):
    index = Index()
    if not dirs:
        dirs = ['.']
    for repo_dir in dirs:
        ctx.ui.info(_('* Building index of PISI files under %s') % repo_dir)
        index.index(repo_dir)
    index.write(output)
    ctx.ui.info(_('* Index file written'))

def add_repo(name, indexuri):
    repo = pisi.repodb.Repo(URI(indexuri))
    ctx.repodb.add_repo(name, repo)
    ctx.ui.info(_('Repo %s added to system.') % name)

def remove_repo(name):
    if ctx.repodb.has_repo(name):
        ctx.repodb.remove_repo(name)
        ctx.ui.info(_('Repo %s removed from system.') % name)
    else:
        ctx.ui.error(_('Repository %s does not exist. Cannot remove.') 
                 % name)

def update_repo(repo):

    ctx.ui.info(_('* Updating repository: %s') % repo)
    index = Index()
    index.read_uri(ctx.repodb.get_repo(repo).indexuri.get_uri(), repo)
    index.update_db(repo)
    ctx.ui.info(_('\n* Package database updated.'))

def delete_cache():
    util.clean_dir(ctx.config.packages_dir())
    util.clean_dir(ctx.config.archives_dir())
    util.clean_dir(ctx.config.tmp_dir())
