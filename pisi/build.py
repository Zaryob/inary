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
from os.path import basename, dirname

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
from pisi.specfile import SpecFile
import pisi.util as util
from pisi.util import join_path as join, parenturi
from pisi.file import File
import pisi.context as ctx
import pisi.dependency as dependency
import pisi.operations as operations
from pisi.sourcearchive import SourceArchive
from pisi.files import Files, FileInfo
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


class Builder:
    """Provides the package build and creation routines"""
    #FIXME: this class and every other class must use URLs as paths!

    def __init__(self, specuri, authinfo = None):

        # process args
        if not isinstance(specuri, URI):
            specuri = URI(specuri)
        if authinfo:
            specuri.set_auth_info(authinfo)

        self.authinfo = authinfo

        # read spec file, we'll need it :)
        self.set_spec_file(specuri)

        if specuri.is_remote_file():
            #make local here and fuck up
            self.specdir = self.fetch_files()
        else:
            self.specdir = dirname(self.specuri.get_uri())

        self.sourceArchive = SourceArchive(self.spec, self.pkg_work_dir())

        self.set_environment_vars()

        self.actionLocals = None
        self.actionGlobals = None
        self.srcDir = None

    def set_spec_file(self, specuri):
        if not specuri.is_remote_file():
            specuri = URI(os.path.realpath(specuri.get_uri()))  # FIXME: doesn't work for file://
        self.specuri = specuri
        spec = SpecFile()
        spec.read(specuri, ctx.config.tmp_dir())
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

    def set_state(self, state):
        stateFile = util.join_path(self.pkg_work_dir(), "pisiBuildState")
        open(stateFile, "w").write(state)

    def get_state(self):
        stateFile = util.join_path(self.pkg_work_dir(), "pisiBuildState")
        if not os.path.exists(stateFile): # no state
            return None
        return open(stateFile, "r").read()

    def build(self):
        """Build the package in one shot."""

        ctx.ui.status(_("Building PISI source package: %s") % self.spec.source.name)
        
        self.compile_action_script()
   
        # check if all patch files exists, if there are missing no need to unpack!
        self.patch_exists()

        self.check_build_dependencies()
        self.fetch_component()
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
            "PKG_DIR": self.pkg_dir(),
            "WORK_DIR": self.pkg_work_dir(),
            "INSTALL_DIR": self.pkg_install_dir(),
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

    def fetch_files(self):
        self.specdiruri = dirname(self.specuri.get_uri())
        pkgname = basename(self.specdiruri)
        self.destdir = join(ctx.config.tmp_dir(), pkgname)
        #self.location = dirname(self.url.uri)

        self.fetch_actionsfile()
        self.fetch_patches()
        self.fetch_comarfiles()
        self.fetch_additionalFiles()

        return self.destdir

    def fetch_actionsfile(self):
        actionsuri = join(self.specdiruri, ctx.const.actions_file)
        self.download(actionsuri, self.destdir)
        
    def fetch_patches(self):
        spec = self.spec
        for patch in spec.source.patches:
            file_name = basename(patch.filename)
            dir_name = dirname(patch.filename)
            patchuri = join(self.specdiruri, 
                            ctx.const.files_dir, dir_name, file_name)
            self.download(patchuri, join(self.destdir, ctx.const.files_dir, dir_name))

    def fetch_comarfiles(self):
        spec = self.spec
        for package in spec.packages:
            for pcomar in package.providesComar:
                comaruri = join(self.specdiruri,
                                ctx.const.comar_dir, pcomar.script)
                self.download(comaruri, join(self.destdir, ctx.const.comar_dir))

    def fetch_additionalFiles(self):
        spec = self.spec
        for pkg in spec.packages:
            for afile in pkg.additionalFiles:
                file_name = basename(afile.filename)
                dir_name = dirname(afile.filename)
                afileuri = join(self.specdiruri, 
                                ctx.const.files_dir, dir_name, file_name)
                self.download(afileuri, join(self.destdir, ctx.const.files_dir, dir_name))

    def download(self, uri, transferdir):
        # fix auth info and download
        uri = File.make_uri(uri)
        if self.authinfo:
            uri.set_auth_info(self.authinfo)
        File.download(uri, transferdir)

    def fetch_component(self):
        if not self.spec.source.partOf:
            ctx.ui.warning(_('PartOf tag not defined, looking for component'))
            diruri = parenturi(self.specuri.get_uri())
            parentdir = parenturi(diruri)
            url = util.join_path(parentdir, 'component.xml')
            progress = ctx.ui.Progress
            if URI(url).is_remote_file():
                fetch_url(url, self.pkg_work_dir(), progress)
                path = util.join_path(self.pkg_work_dir(), 'component.xml')
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
        ctx.ui.info(_("Unpacking archive..."), noln = True)
        self.sourceArchive.unpack()
        ctx.ui.info(_(" unpacked (%s)") % self.pkg_work_dir())
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
        if os.path.exists(self.pkg_install_dir()):
            util.clean_dir(self.pkg_install_dir())
            
        # install function is mandatory!
        self.run_action_function(ctx.const.install_func, True)
        self.set_state("installaction")

    def compile_action_script(self):
        """Compiles actions.py and sets the actionLocals and actionGlobals"""
        scriptfile = util.join_path(self.specdir, ctx.const.actions_file)
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
                    
        return util.join_path(self.pkg_work_dir(), workdir)

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

        build_deps = self.spec.source.buildDependencies

        if not ctx.get_option('bypass_safety'):
            if ctx.componentdb.has_component('system.devel'):
                build_deps_names = set([x.package for x in build_deps])
                devel_deps_names = set(ctx.componentdb.get_component('system.devel').packages)
                extra_names = devel_deps_names - build_deps_names
                extra_names = filter(lambda x: not ctx.installdb.is_installed(x), extra_names)
                if extra_names:
                    ctx.ui.warning(_('Safety switch: following extra packages in system.devel will be installed: ') +
                               util.strlist(extra_names))
                    extra_deps = [dependency.Dependency(package = x) for x in extra_names]
                    build_deps.extend(extra_deps)
                else:
                    ctx.ui.warning(_('Safety switch: system.devel is already installed'))
            else:
                ctx.ui.warning(_('Safety switch: the component system.devel cannot be found'))

        # find out the build dependencies that are not satisfied...
        dep_unsatis = []
        for dep in build_deps:
            if not dependency.installed_satisfies_dep(dep):
                dep_unsatis.append(dep)
    
        if dep_unsatis:
            ctx.ui.info(_("Unsatisfied Build Dependencies:") + ' '
                        + util.strlist([str(x) for x in dep_unsatis]) )
                
            if not ctx.config.get_option('ignore_dependency'):
                for dep in dep_unsatis:
                    if not dependency.repo_satisfies_dep(dep):
                        raise Error(_('Build dependency %s cannot be satisfied') % str(dep))
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

        files_dir = os.path.abspath(util.join_path(self.specdir,
                                                 ctx.const.files_dir))
        for patch in self.spec.source.patches:
            patchFile = util.join_path(files_dir, patch.filename)
            if not os.access(patchFile, os.F_OK):
                raise Error(_("Patch file is missing: %s\n") % patch.filename)

    def apply_patches(self):
        files_dir = os.path.abspath(util.join_path(self.specdir,
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
        install_dir = self.pkg_install_dir()
        pkg_name = self.spec.source.name + '-' + self.spec.source.version + '-' + self.spec.source.release
        try:
            nostrip = self.actionGlobals['NoStrip']
            util.strip_directory(install_dir, pkg_name, nostrip)
        except KeyError:
            util.strip_directory(install_dir, pkg_name)

    def gen_metadata_xml(self, package):
        """Generate the metadata.xml file for build source.

        metadata.xml is composed of the information from specfile plus
        some additional information."""
        metadata = MetaData()
        metadata.from_spec(self.spec.source, package)

        metadata.package.distribution = ctx.config.values.general.distribution
        metadata.package.distributionRelease = ctx.config.values.general.distribution_release
        metadata.package.architecture = "Any"
        
        size, d = 0, self.pkg_install_dir()

        for path in package.files:
             size += util.dir_size(util.join_path(d, path.path))

        metadata.package.installedSize = size

        # build no
        if ctx.config.options.ignore_build_no:
            metadata.package.build = None  # means, build no information n/a
            ctx.ui.warning(_('Build number is not available due to --ignore-build'))
        elif (not ctx.config.values.build.buildno):
            metadata.package.build = None
            ctx.ui.warning(_('Build number is not available. For repo builds you must enable buildno in pisi.conf.'))
        else:
            metadata.package.build = self.calc_build_no(metadata.package.name)

        metadata_xml_path = util.join_path(self.pkg_dir(), ctx.const.metadata_xml)
        metadata.write(metadata_xml_path)
        self.metadata = metadata

    def gen_files_xml(self, package):
        """Generates files.xml using the path definitions in specfile and
        the files produced by the build system."""
        files = Files()
        install_dir = self.pkg_install_dir()

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

        files_xml_path = util.join_path(self.pkg_dir(), ctx.const.files_xml)
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
                    try:
                        old_pkg = Package(old_package_fn, 'r')
                        old_pkg.read(util.join_path(ctx.config.tmp_dir(), 'oldpkg'))
                        ctx.ui.info(_('(found old version %s)') % old_package_fn)
                        if str(old_pkg.metadata.package.name) != package_name:
                            ctx.ui.warning(_('Skipping %s with wrong pkg name ') %
                                           old_package_fn)
                            continue
                        old_build = old_pkg.metadata.package.build
                        found.append( (old_package_fn, old_build) )
                    except:
                        ctx.ui.warning('Package file %s may be corrupt. Skipping.' % old_package_fn)
                        continue

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
                # sort in order of increasing build number
                a.sort(lambda x,y : cmp(x[1],y[1]))
                old_package_fn = a[-1][0]   # get the last one
                old_build = a[-1][1]

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
                            #FIXME: workaround for .a issue, skip .a files
                            if fn.path.endswith('.a') and fn.type=='library':
                                continue
                            if fo.hash != fn.hash:
                                changed = True
                                break
            else: # no old build had a build number
                old_build = None

            ctx.ui.debug('old build number: %s' % old_build)
                            
            # set build number
            if old_build is None:
                ctx.ui.warning(_('(old package lacks a build no, setting build no to 1.)'))
                return 1
            elif changed:
                ctx.ui.info(_('There are changes, incrementing build no to %d') % (old_build + 1))
                return old_build + 1
            else:
                ctx.ui.info(_('There is no change from previous build %d') % old_build)
                return old_build

    def build_packages(self):
        """Build each package defined in PSPEC file. After this process there
        will be .pisi files hanging around, AS INTENDED ;)"""

        self.fetch_component() # bug 856

        # Strip install directory before building .pisi packages.
        self.strip_install_dir()

        package_names = []

        for package in self.spec.packages:
            # store additional files
            c = os.getcwd()
            os.chdir(self.specdir)
            install_dir = self.pkg_dir() + ctx.const.install_dir_suffix
            for afile in package.additionalFiles:
                src = os.path.join(ctx.const.files_dir, afile.filename)
                dest = os.path.join(install_dir + os.path.dirname(afile.target), os.path.basename(afile.target))
                util.copy_file(src, dest)
                if afile.permission:
                    # mode is octal!
                    os.chmod(dest, int(afile.permission, 8))

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
            os.chdir(self.specdir)
            for pcomar in package.providesComar:
                fname = util.join_path(ctx.const.comar_dir,
                                     pcomar.script)
                pkg.add_to_package(fname)

            # add xmls and files
            os.chdir(self.pkg_dir())
        
            pkg.add_to_package(ctx.const.metadata_xml)
            pkg.add_to_package(ctx.const.files_xml)

            # Now it is time to add files to the packages using newly
            # created files.xml
            files = Files()
            files.read(ctx.const.files_xml)
            for finfo in files.list:
                pkg.add_to_package(join("install", finfo.path))

            pkg.close()
            os.chdir(c)
            self.set_state("buildpackages")
            ctx.ui.info(_("Done."))
           
        if ctx.config.values.general.autoclean is True:
            ctx.ui.info(_("Cleaning Build Directory..."))
            util.clean_dir(self.pkg_dir())
        else:
            ctx.ui.info(_("Keeping Build Directory"))

        return package_names


# build functions...

def build(pspecfile, authinfo=None):
    pb = pisi.build.Builder(pspecfile, authinfo)
    return pb.build()

order = {"none": 0,
         "unpack": 1,
         "setupaction": 2,
         "buildaction": 3,
         "installaction": 4,
         "buildpackages": 5}

def __buildState_unpack(pb):
    # unpack is the first state to run.
    pb.fetch_source_archive()
    pb.unpack_source_archive()
    pb.apply_patches()

def __buildState_setupaction(pb, last):

    if order[last] < order["unpack"]:
        __buildState_unpack(pb)
    pb.run_setup_action()

def __buildState_buildaction(pb, last):

    if order[last] < order["setupaction"]:
        __buildState_setupaction(pb, last)
    pb.run_build_action()

def __buildState_installaction(pb, last):
    
    if order[last] < order["buildaction"]:
        __buildState_buildaction(pb, last)
    pb.run_install_action()

def __buildState_buildpackages(pb, last):

    if order[last] < order["installaction"]:
        __buildState_installaction(pb, last)
    pb.build_packages()

def build_until(pspecfile, state, authinfo=None):
    pb = pisi.build.Builder(pspecfile, authinfo)
    pb.compile_action_script()
    
    last = pb.get_state()
    ctx.ui.info("Last state was %s"%last)

    if not last: last = "none"

    if state == "unpack":
        __buildState_unpack(pb)
        return

    if state == "setupaction":
        __buildState_setupaction(pb, last)
        return
    
    if state == "buildaction":
        __buildState_buildaction(pb, last)
        return

    if state == "installaction":
        __buildState_installaction(pb, last)
        return

    __buildState_buildpackages(pb, last)
