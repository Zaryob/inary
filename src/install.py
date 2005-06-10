#import package
from specfile import SpecFile
from package import Package
import util
#import repodb
#import packagedb
#import dependency
#import conflicts


def install_package_file(package_fn):
    
    package = Package(package_fn, "r")
    # extract control files
    util.clean_directory(install_dir)
    package.extract_files(install_dir)

    # verify package
    # check pspec semantics
    
    
    # check file system requirements
    # check conflicts
    # check dependencies

    # unzip package in place

    # update databases

    # installdb
    
