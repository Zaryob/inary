# -*- coding: utf-8 -*-

#import package
from specfile import *
from package import Package
import util
from context import ctx
from ui import ui
import installdb
import packagedb
import dependency
#import conflicts

class InstallError(Exception):
    pass

def install_package_file(package_fn):
    
    package = Package(package_fn, 'r')
    # extract control files
    util.clean_dir(ctx.install_dir())
    ui.info('extracting files\n')
    package.extract_PISI_files(ctx.install_dir())

    # verify package
    # check if we have all required files

    metadata = MetaData()
    metadata.read(ctx.install_dir() + '/metadata.xml')
    # check package semantics
    if not metadata.verify():
        raise InstallError("MetaData format wrong")

    # check file system requirements
    # what to do if / is split into /usr, /var, etc.?
    
    # check conflicts
    # check dependencies

    # unzip package in place

    # update databases

    # installdb
    installdb.install(spec.spec.install_dir() + '/files.xml')

