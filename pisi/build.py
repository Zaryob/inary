# -*- coding: utf-8 -*-
# package bulding stuff
# maintainer: baris and meren

# python standard library
import os
import sys

import util
from ui import ui
from constants import const
from config import config
from sourcearchive import SourceArchive
from files import Files, FileInfo
from specfile import SpecFile
from metadata import MetaData
from package import Package

class PisiBuildError(Exception):
    pass

class PisiBuild:
    """PisiBuild class, provides the package build and creation routines"""
    def __init__(self, buildcontext):
        self.ctx = buildcontext
        self.work_dir = self.ctx.pkg_work_dir()
        self.spec = self.ctx.spec
        self.sourceArchive = SourceArchive(self.ctx)

    def build(self):
        ui.info("Building PISI source package: %s\n" % self.spec.source.name)

        ui.info("Fetching source from: %s\n" % self.spec.source.archiveUri)
        self.sourceArchive.fetch()
        ui.info("Source archive is stored: %s/%s\n"
                %(self.ctx.archives_dir(), self.spec.source.archiveName))
    
        self.solveBuildDependencies()

        ui.info("Unpacking archive...")
        self.sourceArchive.unpack()
        ui.info(" unpacked (%s)\n" % self.ctx.pkg_work_dir())

        self.applyPatches()

        try:
            specdir = os.path.dirname(self.ctx.pspecfile)
            self.actionScript = open("/".join([specdir,const.actions_file])).read()
        except IOError, e:
            ui.error ("Action Script: %s\n" % e)
            return 

        #we'll need this our working directory after actionscript
        #finished its work in the work_dir
        curDir = os.getcwd()

        locals = globals = {}
    
        try:
            exec compile(self.actionScript , "error", "exec") in locals,globals
        except SyntaxError, e:
            ui.error ("Error : %s\n" % e)
            return 
       
        self.goToWorkDir(globals)
       
        self.configureSource(locals)
        self.buildSource(locals)
        self.installSource(locals)

        os.chdir(curDir)
        # after all, we are ready to build/prepare the packages
        self.buildPackages()

    def solveBuildDependencies(self):
        """pre-alpha: fail if dependencies not satisfied"""
        pass

    def applyPatches(self):
        pass

    def goToWorkDir(self, globals):
        path = globals['WorkDir']
        if path:
            path = self.ctx.pkg_work_dir() + "/" + path
        else:
            path = self.ctx.pkg_work_dir() + "/" + \
                self.spec.source.name + "-" + self.spec.source.version
            
        try:
            os.chdir(path)
        except OSError, e:
            ui.error ("No such file or directory: %s\n" % e)
            sys.exit()

    def configureSource(self, locals):
        func = const.setup_func
        if func in locals:
            ui.info("Configuring %s...\n" % self.spec.source.name)
            locals[func]()

    def buildSource(self, locals):
        func = const.build_func
        if func in locals:
            ui.info("Building %s...\n" % self.spec.source.name)
            locals[func]()

    def installSource(self, locals):
        func = const.install_func
        if func in locals:
            ui.info("Installing %s...\n" % self.spec.source.name)
            locals[func]()
        
    def genMetaDataXml(self, package):
        metadata = MetaData()
        metadata.fromSpec(self.spec.source, package)
        metadata.package.distribution = const.distribution
        metadata.package.distributionRelease = const.distributionRelease
        metadata.package.architecture = "Any"
        
        # FIXME: Bu hatalı. installsize'ı almak için tüm
        # pkg_install_dir()'ın boyutunu hesaplayamayız. Bir source
        # birden fazla kaynak üretebilir. package.paths ile
        # karşılaştırarak file listesinden boyutları hesaplatmalıyız.
        d = self.ctx.pkg_install_dir()
        size = util.dir_size(d)
        metadata.package.installedSize = str(size)
        metadata.write(os.path.join(self.ctx.pkg_dir(), const.metadata_xml))

    def genFilesXml(self, package):
        """Generetes files.xml using the path definitions in specfile and
        generated files by the build system."""
        files = Files()
        install_dir = self.ctx.pkg_install_dir()
        for fpath, fhash in util.get_file_hashes(install_dir):
            # get the relative path
            frpath = fpath[len(install_dir):]
            ftype = ""
            # The usage of depth is somewhat confusing. It is used for
            # finding the best match to package.paths. For an example,
            # if package.paths contains
            # ['/usr/share','/usr/share/doc'] and frpath is
            # /usr/share/doc/filename our iteration over package.paths
            # should match the second item.
            depth = 0
            for path in package.paths:
                if frpath.startswith(path.pathname):
                    if depth < len(path.pathname):
                        depth = len(path.pathname)
                        ftype = path.fileType
                        fsize = str(os.path.getsize(fpath))
            files.append(FileInfo(frpath, ftype, fsize, fhash))
        files.write(os.path.join(self.ctx.pkg_dir(), const.files_xml))

    def buildPackages(self):
        for package in self.spec.packages:
            ui.info("** Building package %s\n" % package.name);
            
            ui.info("Generating %s..." % const.metadata_xml)
            self.genMetaDataXml(package)
            ui.info(" done.\n")

            ui.info("Generating %s..." % const.files_xml)
            self.genFilesXml(package)
            ui.info(" done.\n")

            ui.info("Creating PISI package bla bla....\n")
            # testing
            pkgName = package.name + '-' + self.spec.source.version +\
                '-' + self.spec.source.release + ".pisi"
            pkg = Package(pkgName, 'w')
            c = os.getcwd()

            os.chdir(self.ctx.pkg_dir())
            pkg.add_file(const.metadata_xml)
            pkg.add_file(const.files_xml)
            pkg.add_file("install")
            pkg.close()
            os.chdir(c)
