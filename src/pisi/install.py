# -*- coding: utf-8 -*-

#import package
from specfile import *
from package import Package
import util
import ui
import installdb
import packagedb
import dependency
#import conflicts

class InstallError(Exception):
    pass

def install_package_file(package_fn):
    
    package = Package(package_fn, 'r')
    # extract control files
    util.clean_directory(install_dir())
    ui.info('extracting files\n')
    package.extract_files(install_dir())

    # verify package
    # check if we have all required files

    metadata = MetaData()
    metadata.read(install_dir() + '/metadata.xml')
    # check package semantics
    metadata.verify()

    # check file system requirements
    # what to do if / is split into /usr, /var, etc.?
    
    # check conflicts
    # check dependencies

    # unzip package in place

    # update databases

    # installdb
    installdb.install(spec.spec.install_dir() + '/files.xml')
    
