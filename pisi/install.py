# -*- coding: utf-8 -*-
# Package install operation
# Author:  Eray Ozkural <eray@uludag.org.tr>

#import package
from specfile import *
from package import Package
import util
from config import config
from ui import ui
from installdb import installdb
from packagedb import packagedb
import dependency
from metadata import MetaData
#import conflicts

##TODO: Caglar'in onerisi uzerine.
##bunu PisiBuild gibi class yapalim. Asagida yazdigim
##gibi bir test edip nerelere extend edecek ama gorelim
##lutfen. daha hic calismadi bile. :/

class InstallError(Exception):
    pass

def install(package_fn):
    
    package = Package(package_fn, 'r')
    # extract control files
    util.clean_dir(config.install_dir())
    package.extract_PISI_files(config.install_dir())

    # verify package

    # check if we have all required files

    metadata = MetaData()
    metadata.read(os.path.join(config.install_dir(), 'metadata.xml'))
    # check package semantics
    if not metadata.verify():
        raise InstallError("MetaData format wrong")

    # check file system requirements
    # what to do if / is split into /usr, /var, etc.?
    
    # check conflicts
    # check dependencies
    if not dependency.installable(metadata.package.name):
        raise InstallError("Package not installable")

    # unzip package in place
    ui.info('Extracting files\n')
    package.extract_dir_flat('install', config.destdir)
    
    # update databases

    # installdb
    installdb.install(metadata.package.name,
                      metadata.package.version,
                      metadata.package.release,
                      os.path.join(config.install_dir(), 'files.xml'))
