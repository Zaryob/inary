#import package
from specfile import SpecFile
from package import Package
#import repodb
#import packagedb
#import dependency
#import conflicts


def install_package_file(package_fn):
    
    package = Package(package_fn, "r")
    # extract control files
    package.extract_files(tmp_dir + "install/")

    # verify package
    # check file semantics
    # check file system requirements
    # check conflicts
    # check dependencies

    # unzip package in place

    # update databases

    # installdb
    
