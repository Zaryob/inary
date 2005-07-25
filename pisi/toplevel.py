# top level PISI interfaces
# a facade to the entire PISI system

import os

from config import config
from constants import const
from ui import ui
from purl import PUrl
import util

import operations

def install(packages):
    """install a list of packages (either files, urls, or names)"""
    #TODO: this for loop is just a placeholder
    for x in packages:
        operations.install_single(x)

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

