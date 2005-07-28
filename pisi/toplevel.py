# top level PISI interfaces
# a facade to the entire PISI system

import os
import sys

from config import config
from constants import const
from ui import ui
from purl import PUrl
import util
import dependency
import pgraph
import operations
from packagedb import packagedb

def install(packages):
    """install a list of packages (either files/urls, or names)"""
    # determine if this is a list of files/urls or names
    if packages[0].endswith(const.package_prefix): # they all have to!
        install_pkg_files(packages)
    else:
        install_pkg_names(packages)

def install_pkg_files(packages):
    """install a number of pisi package files"""

    # read the package information into memory first
    # regardless of which distribution they come from
    d_t = {}
    for x in packages:
        package = Package(x)
        package.read()
        d_t[package.name] = package.metadata

    # for this case, we have to determine the dependencies
    # that aren't already satisfied and try to install them 
    # from the repository.
    dep_unsatis = []
    for name in d_t.keys():
        pkg = d_t[name]
        deps = pkg.runtimeDeps
        if not dependency.satisfiesDep(pkg, deps):
            dep_unsatis.append(deps)

    # now determine if these unsatisfied dependencies could
    # be satisfied by installing packages from the repo

    # if so, then invoke install_pkg_names
    install_pkg_names([x.package for x in dep_unsatis])

def install_pkg_names(A):
    """This is the real thing. It installs packages from
    the repository, trying to perform a minimum number of
    installs"""
    
    # try to construct a pisi graph of packages to
    # install / reinstall

    G_f = pgraph.PGraph()               # construct G_f

    # find the "install closure" graph of G_f by package 
    # set A using packagedb
    B = A
    state = {}
    while len(B) > 0:
        Bp = set()
        for x in B:
            pkg = packagedb.get_package(x)
            #print pkg
            for dep in pkg.runtimeDeps:
                # we don't deal with satisfied dependencies
                if not dependency.satisfiesDep(pkg, dep):
                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)
        B = Bp
    G_f.write_graphviz(sys.stdout)


def remove(packages):
    #TODO: this for loop is just a placeholder
    for x in packages:
        operations.remove_single(x)


def info(package_name):
    from package import Package

    package = Package(package_name)
    package.read()
    return package.metadata, package.files


def index(repo_dir = '.'):
    from index import Index

    ui.info('* Building index of PISI files under %s\n' % repo_dir)
    index = Index()
    index.index(repo_dir)
    index.write(const.pisi_index)
    ui.info('* Index file written\n')


def updatedb(indexfile = None, repo = "default"):
    from index import Index

    if not indexfile:
        repos_path = config.values.repos[repo]
        indexfile = os.path.join(repos_path, const.pisi_index)

    ui.info('* Updating DB from index file: %s\n' % indexfile)
    index = Index()
    index.read(indexfile, repo)
    index.update_db()
    ui.info('* Package db updated.\n')


def build(pspecfile, authInfo=None):
    from build import PisiBuild

    url = PUrl(pspecfile)
    if url.isRemoteFile():
        from sourcefetcher import SourceFetcher
        fs = SourceFetcher(url, authInfo)
        url.uri = fs.fetch_all()

    pb = PisiBuild(url.uri)
    pb.build()

