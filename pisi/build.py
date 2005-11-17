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
import glob

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.util as util
import pisi.context as ctx
import pisi.dependency as dependency
import pisi.operations as operations
from pisi.sourcearchive import SourceArchive
from pisi.files import Files, File as FileInfo
from pisi.fetcher import fetch_url
from pisi.uri import URI
from pisi.metadata import MetaData
from pisi.package import Package
import pisi.component as component


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
        if util.subpath(pinfo.path, path):
            length = len(pinfo.path)
            if depth < length:
                depth = length
                ftype = pinfo.fileType
    return ftype

def check_path_collision(package, pkgList):
    """This function will check for collision of paths in a package with
    the paths of packages in pkgList. The return value will be the
    list containing the paths that collide."""
    collisions = []
    for pinfo in package.files:
        for pkg in pkgList:
            if pkg is package:
                continue
            for path in pkg.files:
                # if pinfo.path is a subpath of path.path like
                # the example below. path.path is marked as a
                # collide. Exp:
                # pinfo.path: /usr/share
                # path.path: /usr/share/doc
                if util.subpath(pinfo.path, path.path):
                    collisions.append(path.path)
                    ctx.ui.error(_('Path %s belongs in multiple packages') %
                                 path.path)
    return collisions

# a dynamic build context
from pisi.specfile import SpecFile


class BuildContext(object):
    """Build Context"""

    def __init__(self, pspecfile):
        super(BuildContext, self).__init__()
        self.set_spec_file(pspecfile)

    def set_spec_file(self, pspecfile):
        self.pspecfile = pspecfile
        spec = SpecFile()
        spec.read(pspecfile)
        self.spec = spec

    # directory accessor functions
        
    # pkg_x_dir: per package directory for storing info type x

    def pkg_dir(self):
        "package build directory"
        packageDir = self.spec.source.name + '-' + \
                     self.spec.source.version + '-' + self.spec.source.release
        return util.join_path(ctx.config.dest_dir(), ctx.config.values.dirs.tmp_dir,
                     packageDir)
   
    def pkg_work_dir(self):
        return self.pkg_dir() + ctx.const.work_dir_suffix

    def pkg_install_dir(self):
        return self.pkg_dir() + ctx.const.install_dir_suffix


class Builder:
    """Provides the package build and creation routines"""
    def __init__(self, pspec):
        self.bctx = BuildContext(pspec)
        self.pspecdir = os.path.dirname(os.path.realpath(self.bctx.pspecfile))
        self.spec = self.bctx.spec
        self.sourceArchive = SourceArchive(self.bctx)

        self.set_environment_vars()

        self.actionLocals = None
        self.actionGlobals = None
        self.srcDir = None

    def set_state(self, state):
        stateFile = util.join_path(self.bctx.pkg_work_dir(), "pisiBuildState")
        open(stateFile, "w").write(state)

    def get_state(self):
        stateFile = util.join_path(self.bctx.pkg_work_dir(), "pisiBuildState")
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

        self.check_build_dependencies()
        
        self.get_component()
        
        self.fetch_source_archive()
        self.unpack_source_archive()

        # apply the patches and prepare a source directory for build.
        self.apply_patches()

        self.run_setup_action()
        self.run_build_action()
        self.run_install_action()

        # after all, we are ready to build/prepare the packages
        return self.build_packages()

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

        # First check icecream, if not found use ccache, no need to use both
        # together (according to kde-wiki it cause performance loss)
        if os.path.exists("/opt/icecream/bin/gcc"):
            # Add icecream directory for support distributed compiling :)
            os.environ["PATH"] = "/opt/icecream/bin/:" + os.environ["PATH"]
            ctx.ui.info(_("IceCream detected. Make sure your daemon is up and running..."))
        elif os.path.exists("/usr/lib/ccache/bin/gcc"):
            # Add ccache directory for support Compiler Cache :)
            os.environ["PATH"] = "/usr/lib/ccache/bin/:" + os.environ["PATH"]
            ctx.ui.info(_("CCache detected..."))

    def get_component(self):
        if not self.spec.source.partOf:
            ctx.ui.warning(_('PartOf tag not defined, looking for component'))
            parentdir = os.path.realpath(self.pspecdir + '/../')
            url = util.join_path(parentdir, 'component.xml')
            progress = ctx.ui.Progress
            if URI(url).is_remote_file():
                fetch_url(url, self.bctx.pkg_work_dir(), progress)
                path = util.join_path(self.bctx.pkg_work_dir(), 'component.xml')
            else:
                if not os.path.exists(url):
                    raise Exception(_('Cannot find component.xml in upper directory'))
                path = url
            comp = component.Component()
            comp.read(path)
            ctx.ui.info(_('Source is part of %s component') % comp.name)
            self.spec.source.partOf = comp.name
            self.spec.override_tags()

    def fetch_source_archive(self):
        ctx.ui.info(_("Fetching source from: %s") % self.spec.source.archive.uri)
        self.sourceArchive.fetch()
        ctx.ui.info(_("Source archive is stored: %s/%s")
                %(ctx.config.archives_dir(), self.spec.source.archive.name))

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
        scriptfile = util.join_path(specdir, ctx.const.actions_file)
        try:
            localSymbols = globalSymbols = {}
            buf = open(scriptfile).read()
            exec compile(buf, "error", "exec") in localSymbols, globalSymbols
        except IOError, e:
            raise Error(_("Unable to read Action Script (%s): %s") %(scriptfile,e))
        except SyntaxError, e:
            raise Error(_("SyntaxError in Action Script (%s): %s") %(scriptfile,e))

        self.actionLocals = localSymbols
        self.actionGlobals = globalSymbols
        self.srcDir = self.pkg_src_dir()
        
    def pkg_src_dir(self):
        """Returns the real path of WorkDir for an unpacked archive."""
        try:
            workdir = self.actionGlobals['WorkDir']
        except KeyError:
            workdir = self.spec.source.name + "-" + self.spec.source.version
                    
        return util.join_path(self.bctx.pkg_work_dir(), workdir)

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

    def check_build_dependencies(self):
        """fail if dependencies not satisfied"""

        build_deps = set(self.spec.source.buildDependencies)

        if not ctx.get_option('bypass_safety'):
            if ctx.componentdb.has_component('system.devel'):
                build_deps_names = set([x.package for x in build_deps])
                devel_deps_names = set(ctx.componentdb.get_component('system.devel').packages)
                extra_names = devel_deps_names - build_deps_names
                ctx.ui.warning(_('Safety switch: following extra packages in system.devel will be installed: ') +
                           util.strlist(extra_names))
                extra_deps = [dependency.Dependency(package = x) for x in extra_names]
                build_deps = build_deps.union(extra_deps)
            else:
                ctx.ui.warning(_('Safety switch: the component system.devel cannot be found'))

        # find out the build dependencies that are not satisfied...
        dep_unsatis = []
        for dep in build_deps:
            if not dependency.installed_satisfies_dep(dep):
                dep_unsatis.append(dep)
    
        if dep_unsatis:
            ctx.ui.info(_("Unsatisfied Build Dependencies:"))
            for dep in dep_unsatis:
                ctx.ui.warning(dep.package)
            if not ctx.config.get_option('ignore_dependency'):
                if ctx.ui.confirm(
                _('Do you want to install the unsatisfied build dependencies')):
                    ctx.ui.info(_('Installing build dependencies.'))
                    operations.install([dep.package for dep in dep_unsatis])
                else:
                    raise Error(_('Cannot build package due to unsatisfied build dependencies'))
            else:
                ctx.ui.warning(_('Ignoring build dependencies.'))

    def patch_exists(self):
        """check existence of patch files declared in PSPEC"""

        files_dir = os.path.abspath(util.join_path(self.pspecdir,
                                                 ctx.const.files_dir))
        for patch in self.spec.source.patches:
            patchFile = util.join_path(files_dir, patch.filename)
            if not os.access(patchFile, os.F_OK):
                raise Error(_("Patch file is missing: %s\n") % patch.filename)

    def apply_patches(self):
        files_dir = os.path.abspath(util.join_path(self.pspecdir,
                                                 ctx.const.files_dir))

        for patch in self.spec.source.patches:
            patchFile = util.join_path(files_dir, patch.filename)
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
        
        size, d = 0, self.bctx.pkg_install_dir()

        for path in package.files:
             size += util.dir_size(util.join_path(d, path.path))

        metadata.package.installedSize = size

        # build no
        if ctx.config.options.ignore_build_no:
            metadata.package.build = None  # means, build no information n/a
            ctx.ui.warning(_('build number is not available.'))
        else:
            metadata.package.build = self.calc_build_no(metadata.package.name)

        metadata_xml_path = util.join_path(self.bctx.pkg_dir(), ctx.const.metadata_xml)
        metadata.write(metadata_xml_path)
        self.metadata = metadata

    def gen_files_xml(self, package):
        """Generates files.xml using the path definitions in specfile and
        the files produced by the build system."""
        files = Files()
        install_dir = self.bctx.pkg_install_dir()

        # FIXME: We need to expand globs before trying to calculate hashes
        # Not on the fly like now.

        # we'll exclude collisions in get_file_hashes. Having a
        # collisions list is not wrong, we must just handle it :).
        # sure -- exa
        collisions = check_path_collision(package, self.spec.packages)
        # FIXME: material collisions after expanding globs must be
        # reported as errors, and an exception must be raised

        d = {}
        def add_path(path):
            # add the files under material path 
            for fpath, fhash in util.get_file_hashes(path, collisions, install_dir):
                frpath = util.removepathprefix(install_dir, fpath) # relative path
                ftype = get_file_type(frpath, package.files)
                try: # broken links and empty dirs can cause problem
                    fsize = os.path.getsize(fpath)
                except OSError:
                    fsize = None
                d[frpath] = FileInfo(path=frpath, type=ftype, size=fsize, hash=fhash)

        for pinfo in package.files:
            wildcard_path = util.join_path(install_dir, pinfo.path)
            for path in glob.glob(wildcard_path):
                add_path(path)

        for (p, fileinfo) in d.iteritems():
            files.append(fileinfo)

        files_xml_path = util.join_path(self.bctx.pkg_dir(), ctx.const.files_xml)
        files.write(files_xml_path)
        self.files = files

    def calc_build_no(self, package_name):
        """Calculate build number"""

        # find previous build in output dir and packages dir
        found = []        
        def locate_package_names(files):
             for fn in files:
                 fn = fn.decode('utf-8')
                 if util.is_package_name(fn, package_name):
                     old_package_fn = util.join_path(root, fn)
                     ctx.ui.info('(found old version %s)' % old_package_fn)
                     old_pkg = Package(old_package_fn, 'r')
                     old_pkg.read(util.join_path(ctx.config.tmp_dir(), 'oldpkg'))
                     if str(old_pkg.metadata.package.name) != package_name:
                         ctx.ui.warning('Skipping %s with wrong pkg name ' %
                                        old_package_fn)
                         continue
                     old_build = old_pkg.metadata.package.build
                     found.append( (old_package_fn, old_build) )

        for root, dirs, files in os.walk(ctx.config.options.output_dir):
            dirs = [] # don't recurse
            locate_package_names(files)
        for root, dirs, files in os.walk(ctx.config.packages_dir()):
            locate_package_names(files)

        if not found:
            return 1
            ctx.ui.warning(_('(no previous build found, setting build no to 1.)'))
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
            old_pkg.read(util.join_path(ctx.config.tmp_dir(), 'oldpkg'))

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
                ctx.ui.warning(_('(old package lacks a build no, setting build no to 0.)'))
                return 0
            elif changed:
                ctx.ui.info(_('There are changes, incrementing build no to %d') % (old_build + 1))
                return old_build + 1
            else:
                ctx.ui.info(_('There is no change from previous build %d ') % old_build)
                return old_build

    def build_packages(self):
        """Build each package defined in PSPEC file. After this process there
        will be .pisi files hanging around, AS INTENDED ;)"""

        from copy import deepcopy

        # Strip install directory before building .pisi packages.
        self.strip_install_dir()

        package_names = []

        for package in self.spec.packages:
            # store additional files
            c = os.getcwd()
            os.chdir(self.pspecdir)
            install_dir = self.bctx.pkg_dir() + ctx.const.install_dir_suffix
            tmp_aF = []
            for afile in package.additionalFiles:
                destdir = util.join_path(install_dir, os.path.dirname(afile.target))
                for src in glob.glob(util.join_path(ctx.const.files_dir, afile.filename)):
                    tmp_afile_obj = deepcopy(afile)
                    tmp_afile_obj.filename = src[len(ctx.const.files_dir) + 1:]
                    tmp_aF.append(tmp_afile_obj)
                    destfile = os.path.basename(afile.target)
                    if not destfile: destfile = os.path.basename(src)
                    ctx.ui.debug(_("Copying additional file: '%s' to '%s' as '%s'") \
                                                          % (src, destdir, destfile))
                    util.copy_file(src, util.join_path(destdir, destfile))
                    if afile.permission:
                        # mode is octal!
                        os.chmod(util.join_path(destdir, destfile), int(afile.permission, 8))

            package.additionalFiles = tmp_aF

            os.chdir(c)
           
            ctx.ui.action(_("** Building package %s") % package.name);

            ctx.ui.info(_("Generating %s,") % ctx.const.files_xml)
            self.gen_files_xml(package)

            ctx.ui.info(_("Generating %s,") % ctx.const.metadata_xml)
            self.gen_metadata_xml(package)

            ctx.ui.info(_("Creating PISI package %s.") % package.name)

            name = util.package_name(package.name,
                                     self.spec.source.version,
                                     self.spec.source.release,
                                     self.metadata.package.build)
            pkg = Package(name, 'w')
            package_names.append(name)

            # add comar files to package
            os.chdir(self.pspecdir)
            for pcomar in package.providesComar:
                fname = util.join_path(ctx.const.comar_dir,
                                     pcomar.script)
                pkg.add_to_package(fname)

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
           
        if ctx.config.values.general.autoclean is True:
            ctx.ui.info(_("Cleaning Build Directory..."))
            util.clean_dir(self.bctx.pkg_dir())
        else:
            ctx.ui.info(_("Keeping Build Directory"))

        return package_names
