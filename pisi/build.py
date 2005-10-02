# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# package bulding stuff
# maintainer: baris and meren

# python standard library
import os
import sys

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.util as util
import pisi.context as ctx
from pisi.sourcearchive import SourceArchive
from pisi.files import Files, FileInfo
from pisi.metadata import MetaData
from pisi.package import Package


class Error(pisi.Error):
    pass


# Helper Functions
def get_file_type(path, pinfoList):
    """Return the file type of a path according to the given PathInfo
    list"""
    # The usage of depth is somewhat confusing. It is used for finding
    # the best match to paths(in pinfolist). For an example, if paths
    # contain ['/usr/share','/usr/share/doc'] and path is
    # /usr/share/doc/filename our iteration over paths should match
    # the second item.
    depth = 0
    ftype = ""
    path = "/"+path # we need a real path.
    for pinfo in pinfoList:
        if util.subpath(pinfo.pathname, path):
            length = len(pinfo.pathname)
            if depth < length:
                depth = length
                ftype = pinfo.fileType
    return ftype

def check_path_collision(package, pkgList):
    """This function will check for collision of paths in a package with
    the paths of packages in pkgList. The return value will be the
    list containing the paths that collide."""
    collisions = []
    for pinfo in package.paths:
        for pkg in pkgList:
            if pkg is package:
                continue
            for path in pkg.paths:
                # if pinfo.pathname is a subpath of path.pathname like
                # the example below. path.patname is marked as a
                # collide. Exp:
                # pinfo.pathname: /usr/share
                # path.pathname: /usr/share/doc
                if util.subpath(pinfo.pathname, path.pathname):
                    collisions.append(path.pathname)
                    ctx.ui.debug(_('Path %s belongs in multiple packages') %
                             path.pathname)
    return collisions

# a dynamic build context
from pisi.specfile import SpecFile


class BuildContext(object):
    """Build Context Singleton"""

    def __init__(self, pspecfile):
        super(BuildContext, self).__init__()
        self.set_spec_file(pspecfile)

    def set_spec_file(self, pspecfile):
        self.pspecfile = pspecfile
        spec = SpecFile()
        spec.read(pspecfile)
        # FIXME: following checks the integrity but does nothing when it is wrong
        # -gurer
        #spec.verify()    # check pspec integrity
        self.spec = spec

    # directory accessor functions
        
    # pkg_x_dir: per package directory for storing info type x

    def pkg_dir(self):
        "package build directory"
        packageDir = self.spec.source.name + '-' + \
                     self.spec.source.version + '-' + self.spec.source.release

        return ctx.config.destdir + ctx.config.values.dirs.tmp_dir \
               + '/' + packageDir
   
    def pkg_work_dir(self):
        return self.pkg_dir() + ctx.const.work_dir_suffix

    def pkg_install_dir(self):
        return self.pkg_dir() + ctx.const.install_dir_suffix


class PisiBuild:
    """PisiBuild class, provides the package build and creation routines"""
    def __init__(self, pspec):
        self.bctx = BuildContext(pspec)
        self.pspecDir = os.path.dirname(os.path.realpath(self.bctx.pspecfile))
        self.spec = self.bctx.spec
        self.sourceArchive = SourceArchive(self.bctx)

        self.set_environment_vars()

        self.actionLocals = None
        self.actionGlobals = None
        self.srcDir = None

    def set_state(self, state):
        stateFile = os.path.join(self.bctx.pkg_work_dir(), "pisiBuildState")
        open(stateFile, "w").write(state)

    def get_state(self):
        stateFile = os.path.join(self.bctx.pkg_work_dir(), "pisiBuildState")
        if not os.path.exists(stateFile): # no state
            return None
        return open(stateFile, "r").read()

    def build(self):
        """Build the package in one shot."""

        ctx.ui.info(_("Building PISI source package: %s") % self.spec.source.name)
        util.xterm_title(_("Building PISI source package: %s\n") % self.spec.source.name)
        
        self.compile_action_script()
   
        # check if all patch files exists, if there are missing no need to unpack!
        self.patch_exists()
  
        self.fetch_source_archive()

        self.unpack_source_archive()

        self.solve_build_dependencies()

        # apply the patches and prepare a source directory for build.
        self.apply_patches()

        self.run_setup_action()
        self.run_build_action()
        self.run_install_action()

        # after all, we are ready to build/prepare the packages
        self.build_packages()

    def set_environment_vars(self):
        """Sets the environment variables for actions API to use"""
        evn = {
            "PKG_DIR": self.bctx.pkg_dir(),
            "WORK_DIR": self.bctx.pkg_work_dir(),
            "INSTALL_DIR": self.bctx.pkg_install_dir(),
            "SRC_NAME": self.spec.source.name,
            "SRC_VERSION": self.spec.source.version,
            "SRC_RELEASE": self.spec.source.release
            }
        os.environ.update(evn)

    def fetch_source_archive(self):
        ctx.ui.info(_("Fetching source from: %s") % self.spec.source.archiveUri)
        self.sourceArchive.fetch()
        ctx.ui.info(_("Source archive is stored: %s/%s")
                %(ctx.config.archives_dir(), self.spec.source.archiveName))

    def unpack_source_archive(self):
        ctx.ui.info(_("Unpacking archive..."))
        self.sourceArchive.unpack()
        ctx.ui.info(_(" unpacked (%s)") % self.bctx.pkg_work_dir())
        self.set_state("unpack")

    def run_setup_action(self):
        #  Run configure, build and install phase
        ctx.ui.action(_("Setting up source..."))
        self.run_action_function(ctx.const.setup_func)
        self.set_state("setupaction")

    def run_build_action(self):
        ctx.ui.action(_("Building source..."))
        self.run_action_function(ctx.const.build_func)
        self.set_state("buildaction")

    def run_install_action(self):
        ctx.ui.action(_("Installing..."))
        
        # Before install make sure install_dir is clean 
        if os.path.exists(self.bctx.pkg_install_dir()):
            util.clean_dir(self.bctx.pkg_install_dir())
            
        # install function is mandatory!
        self.run_action_function(ctx.const.install_func, True)
        self.set_state("installaction")

    def compile_action_script(self):
        """Compiles actions.py and sets the actionLocals and actionGlobals"""
        specdir = os.path.dirname(self.bctx.pspecfile)
        scriptfile = os.path.join(specdir, ctx.const.actions_file)
        try:
            localSymbols = globalSymbols = {}
            buf = open(scriptfile).read()
            exec compile(buf, "error", "exec") in localSymbols, globalSymbols
        except IOError, e:
            ctx.ui.error(_("Unable to read Action Script (%s): %s") %(scriptfile,e))
            sys.exit(1)
        except SyntaxError, e:
            ctx.ui.error (_("SyntaxError in Action Script (%s): %s") %(scriptfile,e))
            sys.exit(1)

        self.actionLocals = localSymbols
        self.actionGlobals = globalSymbols
        self.srcDir = self.pkg_src_dir()
        
    def pkg_src_dir(self):
        """Returns the real path of WorkDir for an unpacked archive."""
        try:
            workdir = self.actionGlobals['WorkDir']
        except KeyError:
            workdir = self.spec.source.name + "-" + self.spec.source.version
                    
        return os.path.join(self.bctx.pkg_work_dir(), workdir)

    def run_action_function(self, func, mandatory=False):
        """Calls the corresponding function in actions.py. 

        If mandatory parameter is True, and function is not present in
        actionLocals pisi.build.Error will be raised."""
        # we'll need our working directory after actionscript
        # finished its work in the archive source directory.
        curDir = os.getcwd()
        os.chdir(self.srcDir)


        if func in self.actionLocals:
            self.actionLocals[func]()
        else:
            if mandatory:
                Error, _("unable to call function from actions: %s") %func

        os.chdir(curDir)

    def solve_build_dependencies(self):
        """fail if dependencies not satisfied"""
        #TODO: we'll have to do better than plugging a fxn here
        pass

    def patch_exists(self):
        """check existence of patch files declared in PSPEC"""

        files_dir = os.path.abspath(os.path.join(self.pspecDir,
                                                 ctx.const.files_dir))
        for patch in self.spec.source.patches:
            patchFile = os.path.join(files_dir, patch.filename)
            if not os.access(patchFile, os.F_OK):
                raise Error(_("Patch file is missing: %s\n") % patch.filename)

    def apply_patches(self):
        files_dir = os.path.abspath(os.path.join(self.pspecDir,
                                                 ctx.const.files_dir))

        for patch in self.spec.source.patches:
            patchFile = os.path.join(files_dir, patch.filename)
            if patch.compressionType:
                patchFile = util.uncompress(patchFile,
                                            compressType=patch.compressionType,
                                            targetDir=ctx.config.tmp_dir())

            ctx.ui.action(_("* Applying patch: %s") % patch.filename)
            util.do_patch(self.srcDir, patchFile, level=patch.level, target=patch.target)

    def strip_install_dir(self):
        """strip install directory"""
        ctx.ui.action(_("Stripping files.."))
        install_dir = self.bctx.pkg_install_dir()
        try:
            nostrip = self.actionGlobals['NoStrip']
            util.strip_directory(install_dir, nostrip)
        except KeyError:
            util.strip_directory(install_dir)

    def gen_metadata_xml(self, package):
        """Generate the metadata.xml file for build source.

        metadata.xml is composed of the information from specfile plus
        some additional information."""
        metadata = MetaData()
        metadata.from_spec(self.spec.source, package)

        metadata.package.distribution = ctx.config.values.general.distribution
        metadata.package.distributionRelease = ctx.config.values.general.distribution_release
        metadata.package.architecture = "Any"
        
        # FIXME: Bu hatalı. installsize'ı almak için tüm
        # pkg_install_dir()'ın boyutunu hesaplayamayız. Bir source
        # birden fazla kaynak üretebilir. package.paths ile
        # karşılaştırarak file listesinden boyutları hesaplatmalıyız.
        d = self.bctx.pkg_install_dir()
        size = util.dir_size(d)
        metadata.package.installedSize = str(size)
        
        # build no
        if ctx.config.options.ignore_build_no:
            metadata.package.build = None  # means, build no information n/a
            ctx.ui.warning('build number is not available.')
        else:
            metadata.package.build = self.calc_build_no(metadata.package.name)

        metadata_xml_path = os.path.join(self.bctx.pkg_dir(), ctx.const.metadata_xml)
        metadata.write(metadata_xml_path)
        self.metadata = metadata

    def gen_files_xml(self, package):
        """Generetes files.xml using the path definitions in specfile and
        generated files by the build system."""
        files = Files()
        install_dir = self.bctx.pkg_install_dir()

        # we'll exclude collisions in get_file_hashes. Having a
        # collisions list is not wrong, we must just handle it :).
        collisions = check_path_collision(package,
                                          self.spec.packages)

        d = {}
        for pinfo in package.paths:
            path = install_dir + pinfo.pathname
            for fpath, fhash in util.get_file_hashes(path, collisions, install_dir):
                frpath = util.removepathprefix(install_dir, fpath) # relative path
                ftype = get_file_type(frpath, package.paths)
                try: # broken links can cause problem
                    fsize = str(os.path.getsize(fpath))
                except OSError:
                    fsize = "0"
                d[frpath] = FileInfo(frpath, ftype, fsize, fhash)
        for (p, fileinfo) in d.iteritems():
            files.append(fileinfo)

        files_xml_path = os.path.join(self.bctx.pkg_dir(), ctx.const.files_xml)
        files.write(files_xml_path)
        self.files = files

    def calc_build_no(self, package_name):
        """Calculate build number"""

        def found_package(fn):
            "did we find the filename we were looking for?"
            if fn.startswith(package_name + '-'):
                if fn.endswith(ctx.const.package_prefix):
                    # get version string, skip separator '-'
                    verstr = fn[len(package_name) + 1:
                                len(fn)-len(ctx.const.package_prefix)]
                    import string
                    for x in verstr.split('-'):
                        # weak rule: version components start with a digit
                        if x is '' or (not x[0] in string.digits):
                            return False
                    return True
            return False

        # find previous build in ctx.config.options.output_dir
        found = []
#        for root, dirs, files in os.walk(ctx.config.options.output_dir):
#             for fn in files:
#                 fn = fn.decode('utf-8')
#                 if found_package(fn):
#                     old_package_fn = os.path.join(root, fn)
#                     ctx.ui.info('(found old version %s)' % old_package_fn)
#                     old_pkg = Package(old_package_fn, 'r')
#                     old_pkg.read(os.path.join(ctx.config.tmp_dir(), 'oldpkg'))
#                     if str(old_pkg.metadata.package.name) != package_name:
#                         ctx.ui.warning('Skipping %s with wrong pkg name ' %
#                                        old_package_fn)
#                         continue
#                     old_build = old_pkg.metadata.package.build
#                     found.append( (old_package_fn, old_build) )
#
# FIXME: Following dirty lines of code just search in the output_dir and
# packages dir for previous packages. But we should find a neat way
# for this...
        files = []
        for f in os.listdir(ctx.config.options.output_dir):
            fp = os.path.join(ctx.config.options.output_dir, f)
            if os.path.isfile(fp):
                files.append(fp)

        packages_dir = ctx.config.packages_dir()
        # FIXME: packages_dir() should be there!
        if not os.path.exists(packages_dir):
            os.makedirs(packages_dir)
        for f in os.listdir(packages_dir):
            fp = os.path.join(packages_dir, f)
            if os.path.isfile(fp):
                files.append(fp)

        for fn in files:
            fn = fn.decode('utf-8')
            if found_package(os.path.basename(fn)):
                old_package_fn = fn
                ctx.ui.info('(found old version %s)' % old_package_fn)
                old_pkg = Package(old_package_fn, 'r')
                old_pkg.read(os.path.join(ctx.config.tmp_dir(), 'oldpkg'))
                if str(old_pkg.metadata.package.name) != package_name:
                    ctx.ui.warning('Skipping %s with wrong pkg name ' %
                                   old_package_fn)
                    continue
                old_build = old_pkg.metadata.package.build
                found.append( (old_package_fn, old_build) )
        if not found:
            return 0
            ctx.ui.warning('(no previous build found, setting build no to 0.)')
        else:
            a = filter(lambda (x,y): y != None, found)
            ctx.ui.debug(str(a))
            if a:
                a.sort(lambda x,y : cmp(x[1],y[1]))
                old_package_fn = a[0][0]
                old_build = a[0][1]
            else:
                old_build = None

            # compare old files.xml with the new one..
            old_pkg = Package(old_package_fn, 'r')
            old_pkg.read(os.path.join(ctx.config.tmp_dir(), 'oldpkg'))

            # FIXME: TAKE INTO ACCOUNT MINOR CHANGES IN METADATA
            changed = False
            fnew = self.files.list
            fold = old_pkg.files.list
            fold.sort(lambda x,y : cmp(x.path,y.path))
            fnew.sort(lambda x,y : cmp(x.path,y.path))
            if len(fnew) != len(fold):
                changed = True
            else:
                for i in range(len(fold)):
                    fo = fold.pop(0)
                    fn = fnew.pop(0)
                    if fo.path != fn.path:
                        changed = True
                        break
                    else:
                        if fo.hash != fn.hash:
                            changed = True
                            break

            # set build number
            if old_build is None:
                ctx.ui.warning('(old package lacks a build no, setting build no to 0.)')
                return 0
            elif changed:
                ctx.ui.info('There are changes, incrementing build no to %d' % (old_build + 1))
                return old_build + 1
            else:
                ctx.ui.info('There is no change from previous build %d ' % old_build)                
                return old_build

    def build_packages(self):
        """Build each package defined in PSPEC file. After this process there
        will be .pisi files hanging around, AS INTENDED ;)"""

        # Strip install directory before building .pisi packages.
        self.strip_install_dir()

        for package in self.spec.packages:

            # store additional files
            c = os.getcwd()
            os.chdir(self.pspecDir)
            install_dir = self.bctx.pkg_dir() + ctx.const.install_dir_suffix
            for afile in package.additionalFiles:
                src = os.path.join(ctx.const.files_dir, afile.filename)
                dest = os.path.join(install_dir + os.path.dirname(afile.target), os.path.basename(afile.target))
                util.copy_file(src, dest)
                if afile.permission:
                    # mode is octal!
                    os.chmod(dest, int(afile.permission, 8))

            os.chdir(c)

            name = util.package_name(package.name,
                                     self.spec.source.version,
                                     self.spec.source.release)
            
            ctx.ui.action(_("** Building package %s") % package.name);

            ctx.ui.info(_("Generating %s,") % ctx.const.files_xml)
            self.gen_files_xml(package)
           
            ctx.ui.info(_("Generating %s,") % ctx.const.metadata_xml)
            self.gen_metadata_xml(package)

            ctx.ui.info(_("Creating PISI package %s.") % name)

            pkg = Package(name, 'w')

            # add comar files to package
            os.chdir(self.pspecDir)
            for pcomar in package.providesComar:
                fname = os.path.join(ctx.const.comar_dir,
                                     pcomar.script)
                pkg.add_to_package(fname)

            # add {post,pre}{install,remove} scripts to package if exists
            prefix_list = [".preinstall", ".preremove", \
                           ".postinstall", ".preinstall"]

            for file in prefix_list:
                filename = package.name + file
                if os.path.exists(filename):
                    pkg.add_to_package(filename)
                    ctx.ui.info(_("%s added to PISI package %s.") % (filename, name))

            # add xmls and files
            os.chdir(self.bctx.pkg_dir())
        
            pkg.add_to_package(ctx.const.metadata_xml)
            pkg.add_to_package(ctx.const.files_xml)

            # Now it is time to add files to the packages using newly
            # created files.xml
            files = Files()
            files.read(ctx.const.files_xml)
            for finfo in files.list:
                pkg.add_to_package("install/" + finfo.path)

            pkg.close()
            os.chdir(c)
            self.set_state("buildpackages")
            util.xterm_title_reset()
            ctx.ui.info(_("Done."))
