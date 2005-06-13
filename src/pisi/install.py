# -*- coding: utf-8 -*-

#import package
from specfile import SpecFile
from package import Package
import util
import ui
import installdb
import packagedb
import dependency
#import conflicts


def install_package_file(package_fn):
    
    package = Package(package_fn, "r")
    # extract control files
    util.clean_directory(install_dir)
    ui.info.("extracting files\n")
    package.extract_files(install_dir)

    # verify package
    # check if we have all required files

    spec = PackageSpecFile()
    spec.read(install_dir + '/pspec.xml')
    # check pspec semantics
    spec.verify()
    # check file system requirements
    # check conflicts
    # check dependencies

    # unzip package in place

    # update databases
    installdb.install(spec.install_dir + '/files.xml')

    # installdb
    
