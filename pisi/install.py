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

##TODO: Caglar'in onerisi uzerine.
##bunu PisiBuild gibi class yapalim. Asagida yazdigim
##gibi bir test edip nerelere extend edecek ama gorelim
##lutfen. daha hic calismadi bile. :/

##alternatif olarak bunu muhtemelen ops diye bir module'e
##tasimak
##daha iyi olabilir. install/remove/upgrade islemlerinin
##oldugu, ya da boyle ayrik kalabilir, ne ne kadar tutuyor
##daha belli degil...

class InstallError(Exception):
    pass

def install(self, package_fn):
    
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
    if not dependency.installable(metadata.packages[0].name):
        raise InstallError("Package not installable")

    # unzip package in place
    package.extract_dir_flat(ctx.destdir)
	
    # update databases

    # installdb
    installdb.install(metadata.packages[0].name,
                      metadata.source.version,
                      metadata.source.release,
                      ctx.install_dir() + '/files.xml')

