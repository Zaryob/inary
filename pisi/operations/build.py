# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2011, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

"""package building code"""

# python standard library
import os
import re
import glob
import stat
import pwd
import grp
import fnmatch

import gettext
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi
import pisi.specfile
import pisi.util as util
import pisi.file
import pisi.context as ctx
import pisi.dependency as dependency
import pisi.api
import pisi.sourcearchive
import pisi.files
import pisi.fetcher
import pisi.uri
import pisi.metadata
import pisi.package
import pisi.component as component
import pisi.archive as archive
import pisi.actionsapi.variables
import pisi.db


class Error(pisi.Error):
    pass

class ActionScriptException(Error):
    pass

class AbandonedFilesException(pisi.Error):
    pass

class ExcludedArchitectureException(Error):
    pass


# Helper Functions
def get_file_type(path, pinfo_list):
    """Return the file type of a path according to the given PathInfo
    list"""

    path = "/%s" % path
    info = None
    glob_match = parent_match = None

    for pinfo in pinfo_list:
        if path == pinfo.path:
            info = pinfo
            break

        elif fnmatch.fnmatch(path, pinfo.path):
            glob_match = pinfo

        elif fnmatch.fnmatch(path, util.join_path(pinfo.path, "*")):
            if parent_match is None or parent_match.path < pinfo.path:
                parent_match = pinfo

    else:
        info = glob_match or parent_match

    return info.fileType, info.permanent

def check_path_collision(package, pkgList):
    """This function will check for collision of paths in a package with
    the paths of packages in pkgList. The return value will be the
    list containing the paths that collide."""
    create_static = ctx.get_option("create_static")
    create_debug = ctx.config.values.build.generatedebug
    ar_suffix = ctx.const.ar_file_suffix
    debug_suffix = ctx.const.debug_file_suffix

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

                if (create_static and path.path.endswith(ar_suffix)) or \
                        (create_debug and path.path.endswith(debug_suffix)):
                    # don't throw collision error for these files.
                    # we'll handle this in gen_files_xml..
                    continue

                if util.subpath(pinfo.path, path.path):
                    collisions.append(path.path.rstrip("/"))
                    ctx.ui.debug(_('Path %s belongs in multiple packages') %
                                 path.path)
    return collisions

def exclude_special_files(filepath, fileinfo, ag):
    keeplist = ag.get("KeepSpecial", [])
    patterns = {"libtool": "libtool library file",
                "python":  "python.*byte-compiled",
                "perl":    "Perl POD document text"}

    if "libtool" in keeplist:
        # Some upstream sources have buggy libtool and ltmain.sh with them,
        # which causes wrong path entries in *.la files. And these wrong path
        # entries sometimes triggers compile-time errors or linkage problems.
        # Instead of patching all these buggy sources and maintain these
        # patches, PiSi removes wrong paths...
        if re.match(patterns["libtool"], fileinfo) and \
                not os.path.islink(filepath):
            ladata = file(filepath).read()
            new_ladata = re.sub("-L%s/\S*" % ctx.config.tmp_dir(), "", ladata)
            new_ladata = re.sub("%s/\S*/install/" % ctx.config.tmp_dir(), "/",
                                new_ladata)
            if new_ladata != ladata:
                file(filepath, "w").write(new_ladata)

    for name, pattern in patterns.items():
        if name in keeplist:
            continue

        if re.match(pattern, fileinfo):
            ctx.ui.debug("Removing special %s file: %s" % (name, filepath))
            os.unlink(filepath)
            # Remove dir if it becomes empty (Bug #11588)
            util.rmdirs(os.path.dirname(filepath))

def strip_debug_action(filepath, fileinfo, install_dir, ag):
    excludelist = tuple(ag.get("NoStrip", []))

    # real path in .pisi package
    path = '/' + util.removepathprefix(install_dir, filepath)

    if path.startswith(excludelist):
        return

    outputpath = util.join_path(os.path.dirname(install_dir),
                                ctx.const.debug_dir_suffix,
                                ctx.const.debug_files_suffix,
                                path)

    if util.strip_file(filepath, fileinfo, outputpath):
        ctx.ui.debug("%s [%s]" % (path, "stripped"))

class Builder:
    """Provides the package build and creation routines"""
    #FIXME: this class and every other class must use URLs as paths!

    @staticmethod
    def from_name(name):
        repodb = pisi.db.repodb.RepoDB()
        sourcedb = pisi.db.sourcedb.SourceDB()
        # download package and return an installer object
        # find package in repository
        sf, reponame = sourcedb.get_spec_repo(name)
        src = sf.source
        if src:

            src_uri = pisi.uri.URI(src.sourceURI)
            if src_uri.is_absolute_path():
                src_path = str(src_uri)
            else:
                repo = repodb.get_repo(reponame)
                #FIXME: don't use dirname to work on URLs
                src_path = os.path.join(
                                    os.path.dirname(repo.indexuri.get_uri()),
                                    str(src_uri.path()))

            ctx.ui.debug(_("Source URI: %s") % src_path)

            return Builder(src_path)
        else:
            raise Error(_("Source %s not found in any active repository.")
                        % name)

    def __init__(self, specuri):

        self.componentdb = pisi.db.componentdb.ComponentDB()
        self.installdb = pisi.db.installdb.InstallDB()

        # process args
        if not isinstance(specuri, pisi.uri.URI):
            specuri = pisi.uri.URI(specuri)

        # read spec file, we'll need it :)
        self.set_spec_file(specuri)

        if specuri.is_remote_file():
            self.specdir = self.fetch_files()
        else:
            self.specdir = os.path.dirname(self.specuri.get_uri())

        # Don't wait until creating .pisi file for complaining about versioning
        # scheme errors
        self.check_versioning(self.spec.getSourceVersion(),
                              self.spec.getSourceRelease())

        # Check package format
        self.target_package_format = ctx.get_option("package_format") \
                                        or pisi.package.Package.default_format

        self.read_translations(self.specdir)

        self.sourceArchives = pisi.sourcearchive.SourceArchives(self.spec)

        self.build_types = self.get_build_types()

        # Use an empty string for the default build
        self.set_build_type("")

        self.check_paths()

        self.actionLocals = None
        self.actionGlobals = None

        self.delta_history_search_paths = []
        self.delta_search_paths = {}

        self.new_packages = []
        self.new_debug_packages = []

        self.delta_map = {}

    def set_spec_file(self, specuri):
        if not specuri.is_remote_file():
            # FIXME: doesn't work for file://
            specuri = pisi.uri.URI(os.path.realpath(specuri.get_uri()))
        self.specuri = specuri
        spec = pisi.specfile.SpecFile()
        spec.read(self.specuri, ctx.config.tmp_dir())
        self.spec = spec

    def read_translations(self, specdir):
        self.spec.read_translations(util.join_path(specdir,
                                    ctx.const.translations_file))

    def package_filename(self, package_info, release_info=None,
                         distro_id=None, with_extension=True):

        if release_info is None:
            release_info = self.spec.history[0]

        if distro_id is None:
            distro_id = ctx.config.values.general.distribution_id

        fn = "-".join((package_info.name,
                       release_info.version,
                       release_info.release,
                       distro_id,
                       package_info.architecture))

        if with_extension:
            fn += ctx.const.package_suffix

        return fn

    # directory accessor functions

    # pkg_x_dir: per package directory for storing info type x

    def pkg_dir(self):
        "package build directory"
        packageDir = self.spec.source.name + '-' + \
                     self.spec.getSourceVersion() + '-' + \
                     self.spec.getSourceRelease()
        return util.join_path(ctx.config.dest_dir(),
                              ctx.config.values.dirs.tmp_dir,
                              packageDir)

    def pkg_work_dir(self):
        suffix = "-%s" % self.build_type if self.build_type else ""
        return self.pkg_dir() + ctx.const.work_dir_suffix + suffix

    def pkg_debug_dir(self):
        return self.pkg_dir() + ctx.const.debug_dir_suffix

    def pkg_install_dir(self):
        return self.pkg_dir() + ctx.const.install_dir_suffix

    def set_state(self, state):
        stateFile = util.join_path(self.pkg_work_dir(), "pisiBuildState")
        open(stateFile, "w").write(state)

    def get_state(self):
        stateFile = util.join_path(self.pkg_work_dir(), "pisiBuildState")
        if not os.path.exists(stateFile):  # no state
            return None
        return open(stateFile, "r").read()

    def build(self):
        """Build the package in one shot."""

        architecture = ctx.config.values.general.architecture
        if architecture in self.spec.source.excludeArch:
            raise ExcludedArchitectureException(
                    _("pspec.xml avoids this package from building for '%s'")
                    % architecture)

        ctx.ui.status(_("Building source package: %s")
                      % self.spec.source.name)

        self.compile_comar_script()

        # check if all patch files exists, if there are missing no need
        # to unpack!
        self.check_patches()

        self.check_build_dependencies()
        self.fetch_component()
        self.fetch_source_archives()

        for build_type in self.build_types:
            self.set_build_type(build_type)
            self.unpack_source_archives()

            self.run_setup_action()
            self.run_build_action()
            if ctx.get_option('debug') and not ctx.get_option('ignore_check'):
                self.run_check_action()
            self.run_install_action()

        # after all, we are ready to build/prepare the packages
        self.build_packages()

    def get_build_types(self):
        ignored_build_types = \
                ctx.config.values.build.ignored_build_types.split(",")
        build_types = [""]
        packages = []

        for package in self.spec.packages:
            if package.buildType:
                if package.buildType in ignored_build_types:
                    continue

                if package.buildType not in build_types:
                    build_types.append(package.buildType)

            packages.append(package)

        self.spec.packages = packages

        return build_types

    def set_build_type(self, build_type):
        if build_type:
            ctx.ui.action(_("Rebuilding for %s") % build_type)

        self.build_type = build_type
        self.set_environment_vars()
        self.load_action_script()

    def set_environment_vars(self):
        """Sets the environment variables for actions API to use"""

        # Each time a builder is created we must reset
        # environment. See bug #2575
        pisi.actionsapi.variables.initVariables()

        env = {"PKG_DIR": self.pkg_dir(),
               "WORK_DIR": self.pkg_work_dir(),
               "INSTALL_DIR": self.pkg_install_dir(),
               "PISI_BUILD_TYPE": self.build_type,
               "SRC_NAME": self.spec.source.name,
               "SRC_VERSION": self.spec.getSourceVersion(),
               "SRC_RELEASE": self.spec.getSourceRelease()}
        os.environ.update(env)

        # First check icecream, if not found use ccache, no need to use both
        # together (according to kde-wiki it cause performance loss)
        if ctx.config.values.build.buildhelper == "icecream":
            if os.path.exists("/opt/icecream/bin/gcc"):
                # Add icecream directory for support distributed compiling :)
                os.environ["PATH"] = "/opt/icecream/bin:%(PATH)s" % os.environ
                ctx.ui.info(_("IceCream detected. Make sure your daemon "
                              "is up and running..."))
        elif ctx.config.values.build.buildhelper == "ccache":
            if os.path.exists("/usr/lib/ccache/bin/gcc"):
                # Add ccache directory for support Compiler Cache :)
                os.environ["PATH"] = "/usr/lib/ccache/bin:%(PATH)s" \
                                                                % os.environ
                # Force ccache to use /root/.ccache instead of $HOME/.ccache
                # which can be modified through actions.py
                os.environ["CCACHE_DIR"] = "/root/.ccache"
                ctx.ui.info(_("CCache detected..."))

    def fetch_files(self):
        self.specdiruri = os.path.dirname(self.specuri.get_uri())
        pkgname = os.path.basename(self.specdiruri)
        self.destdir = util.join_path(ctx.config.tmp_dir(), pkgname)
        #self.location = os.path.dirname(self.url.uri)

        self.fetch_actionsfile()
        self.check_build_dependencies()
        self.fetch_translationsfile()
        self.fetch_patches()
        self.fetch_comarfiles()
        self.fetch_additionalFiles()

        return self.destdir

    def fetch_pspecfile(self):
        pspecuri = util.join_path(self.specdiruri, ctx.const.pspec_file)
        self.download(pspecuri, self.destdir)

    def fetch_actionsfile(self):
        actionsuri = util.join_path(self.specdiruri, ctx.const.actions_file)
        self.download(actionsuri, self.destdir)

    def fetch_translationsfile(self):
        translationsuri = util.join_path(self.specdiruri,
                                         ctx.const.translations_file)
        try:
            self.download(translationsuri, self.destdir)
        except pisi.fetcher.FetchError:
            # translations.xml is not mandatory for PiSi
            pass

    def fetch_patches(self):
        for patch in self.spec.source.patches:
            dir_name = os.path.dirname(patch.filename)
            patchuri = util.join_path(self.specdiruri,
                                      ctx.const.files_dir,
                                      patch.filename)
            self.download(patchuri, util.join_path(self.destdir,
                                                   ctx.const.files_dir,
                                                   dir_name))

    def fetch_comarfiles(self):
        for package in self.spec.packages:
            for pcomar in package.providesComar:
                comaruri = util.join_path(self.specdiruri,
                                ctx.const.comar_dir, pcomar.script)
                self.download(comaruri, util.join_path(self.destdir,
                                                       ctx.const.comar_dir))

    def fetch_additionalFiles(self):
        for pkg in self.spec.packages + [self.spec.source]:
            for afile in pkg.additionalFiles:
                file_name = os.path.basename(afile.filename)
                dir_name = os.path.dirname(afile.filename)
                afileuri = util.join_path(self.specdiruri,
                                ctx.const.files_dir, dir_name, file_name)
                self.download(afileuri, util.join_path(self.destdir,
                                                       ctx.const.files_dir,
                                                       dir_name))

    def download(self, uri, transferdir):
        # fix auth info and download
        uri = pisi.file.File.make_uri(uri)
        pisi.file.File.download(uri, transferdir)

    def fetch_component(self):
        if self.spec.source.partOf:
            return

        ctx.ui.info(_('PartOf tag not defined, looking for component'))
        diruri = util.parenturi(self.specuri.get_uri())
        parentdir = util.parenturi(diruri)
        url = util.join_path(parentdir, 'component.xml')
        progress = ctx.ui.Progress
        if pisi.uri.URI(url).is_remote_file():
            try:
                pisi.fetcher.fetch_url(url, self.pkg_work_dir(), progress)
            except pisi.fetcher.FetchError:
                ctx.ui.warning(_("Cannot find component.xml in remote "
                                 "directory, Source is now part of "
                                 "unknown component"))
                self.spec.source.partOf = 'unknown'
                return
            path = util.join_path(self.pkg_work_dir(), 'component.xml')
        else:
            if not os.path.exists(url):
                ctx.ui.warning(_("Cannot find component.xml in upper "
                                 "directory, Source is now part of "
                                 "unknown component"))
                self.spec.source.partOf = 'unknown'
                return
            path = url
        comp = component.CompatComponent()
        comp.read(path)
        ctx.ui.info(_('Source is part of %s component') % comp.name)
        self.spec.source.partOf = comp.name

    def fetch_source_archives(self):
        self.sourceArchives.fetch()

    def unpack_source_archives(self):
        ctx.ui.action(_("Unpacking archive(s)..."))
        self.sourceArchives.unpack(self.pkg_work_dir())
        # apply the patches and prepare a source directory for build.
        if self.apply_patches():
            # Grab AdditionalFiles
            self.copy_additional_source_files()
            ctx.ui.info(_(" unpacked (%s)") % self.pkg_work_dir())
            self.set_state("unpack")

    def run_setup_action(self):
        #  Run configure, build and install phase
        ctx.ui.action(_("Setting up source..."))
        if self.run_action_function(ctx.const.setup_func):
            self.set_state("setupaction")

    def run_build_action(self):
        ctx.ui.action(_("Building source..."))
        if self.run_action_function(ctx.const.build_func):
            self.set_state("buildaction")

    def run_check_action(self):
        ctx.ui.action(_("Testing package..."))
        self.run_action_function(ctx.const.check_func)

    def run_install_action(self):
        ctx.ui.action(_("Installing..."))

        # Before the default install make sure install_dir is clean
        if not self.build_type and os.path.exists(self.pkg_install_dir()):
            util.clean_dir(self.pkg_install_dir())

        # install function is mandatory!
        if self.run_action_function(ctx.const.install_func, True):
            self.set_state("installaction")

    def get_abandoned_files(self):
        # return the files those are not collected from the install dir

        install_dir = self.pkg_install_dir()
        abandoned_files = []
        all_paths_in_packages = []

        for package in self.spec.packages:
            for path in package.files:
                path = util.join_path(install_dir, path.path)
                all_paths_in_packages.append(path)

        def is_included(path1, path2):
            "Return True if path2 includes path1"
            return path1 == path2 \
                    or fnmatch.fnmatch(path1, path2) \
                    or fnmatch.fnmatch(path1, util.join_path(path2, "*"))

        for root, dirs, files in os.walk(install_dir):
            if not dirs and not files:
                for _path in all_paths_in_packages:
                    if is_included(root, _path):
                        break
                else:
                    abandoned_files.append(root)

            for file_ in files:
                fpath = util.join_path(root, file_)
                for _path in all_paths_in_packages:
                    if is_included(fpath, _path):
                        break

                else:
                    abandoned_files.append(fpath)

        len_install_dir = len(install_dir)
        return map(lambda x: x[len_install_dir:], abandoned_files)

    def copy_additional_source_files(self):
        # store additional files
        for afile in self.spec.source.additionalFiles:
            src = os.path.join(self.specdir, ctx.const.files_dir, afile.filename)
            dest = os.path.join(self.pkg_src_dir(), afile.target)
            util.copy_file(src, dest)
            if afile.permission:
                # mode is octal!
                os.chmod(dest, int(afile.permission, 8))

    def compile_action_script(self):
        """Compiles the action script and returns a code object"""

        fname = util.join_path(self.specdir, ctx.const.actions_file)
        try:
            buf = open(fname).read()
            return compile(buf, fname, "exec")
        except IOError, e:
            raise Error(_("Unable to read Actions Script (%s): %s")
                        % (fname, e))
        except SyntaxError, e:
            raise Error(_("SyntaxError in Actions Script (%s): %s")
                        % (fname, e))

    def load_action_script(self):
        """Compiles and executes the action script"""

        compiled_script = self.compile_action_script()

        try:
            localSymbols = globalSymbols = {}
            exec compiled_script in localSymbols, globalSymbols
        except Exception, e:
            import traceback
            traceback.print_exc(e)
            raise ActionScriptException

        self.actionLocals = localSymbols
        self.actionGlobals = globalSymbols

    def compile_comar_script(self):
        """Compiles comar scripts to check syntax errors"""
        for package in self.spec.packages:
            for pcomar in package.providesComar:
                fname = util.join_path(self.specdir, ctx.const.comar_dir,
                                     pcomar.script)

                try:
                    buf = open(fname).read()
                    compile(buf, "error", "exec")
                except IOError, e:
                    raise Error(_("Unable to read COMAR script (%s): %s")
                                % (fname, e))
                except SyntaxError, e:
                    raise Error(_("SyntaxError in COMAR file (%s): %s")
                                % (fname, e))

    def pkg_src_dir(self):
        """Returns the real path of WorkDir for an unpacked archive."""

        dirname = self.actionGlobals.get("WorkDir")
        if dirname:
            return util.join_path(self.pkg_work_dir(), dirname)

        dirname = self.spec.source.name + "-" + self.spec.getSourceVersion()
        src_dir = util.join_path(self.pkg_work_dir(), dirname)

        if not os.path.exists(src_dir):
            archive = self.spec.source.archive[0]

            # For binary types, WorkDir is usually "."
            if archive.type == "binary":
                return self.pkg_work_dir()

            basename = os.path.basename(archive.uri)
            dirname = os.path.splitext(basename)[0]
            src_dir = util.join_path(self.pkg_work_dir(), dirname)

            while not os.path.exists(src_dir):
                src_dir, ext = os.path.splitext(src_dir)
                if not ext:
                    break

        return src_dir

    def log_sandbox_violation(self, operation, path, canonical_path):
        ctx.ui.error(_("Sandbox violation: %s (%s -> %s)") % (operation,
                                                              path,
                                                              canonical_path))

    def run_action_function(self, func, mandatory=False):
        """Calls the corresponding function in actions.py.

        If mandatory parameter is True, and function is not present in
        actionLocals pisi.build.Error will be raised."""
        # we'll need our working directory after actionscript
        # finished its work in the archive source directory.
        curDir = os.getcwd()
        src_dir = self.pkg_src_dir()
        if os.path.exists(src_dir):
            os.chdir(src_dir)
        else:
            raise Error(_("ERROR: WorkDir (%s) does not exist\n") % src_dir)

        if func in self.actionLocals:
            if ctx.get_option('ignore_sandbox') or \
                    not ctx.config.values.build.enablesandbox:
                self.actionLocals[func]()
            else:
                import catbox

                ctx.ui.info(_("Sandbox enabled build..."))

                # Configure allowed paths from sandbox.conf
                valid_paths = [self.pkg_dir()]
                conf_file = ctx.const.sandbox_conf
                if os.path.exists(conf_file):
                    for line in file(conf_file):
                        line = line.strip()
                        if len(line) > 0 and not line.startswith("#"):
                            if line.startswith("~"):
                                line = os.environ["HOME"] + line[1:]
                            valid_paths.append(line)

                # Extra path for ccache when needed
                if ctx.config.values.build.buildhelper == "ccache":
                    valid_paths.append(os.environ.get("CCACHE_DIR",
                                                      "/root/.ccache"))

                ret = catbox.run(self.actionLocals[func],
                                 valid_paths,
                                 logger=self.log_sandbox_violation)
                # Retcode can be 0 while there is a sanbox violation, so only
                # look for violations to correctly handle it
                if ret.violations != []:
                    ctx.ui.error(_("Sandbox violation result:"))
                    for result in ret.violations:
                        ctx.ui.error("* %s (%s -> %s)" % (result[0],
                                                          result[1],
                                                          result[2]))
                    raise Error(_("Sandbox violations!"))

                if ret.code == 1:
                    raise ActionScriptException
        else:
            if mandatory:
                raise Error(_("unable to call function from actions: %s")
                            % func)

        os.chdir(curDir)
        return True

    def check_paths(self):
        paths = []

        for package in self.spec.packages:
            for path_info in package.files:
                path = os.path.normpath(path_info.path)

                if not path.startswith("/"):
                    raise Error(_("Path must start with a slash: "
                                  "%s") % path_info.path)

                if path in paths:
                    raise Error(_("Multiple 'Path' tags specified "
                                  "for this path: %s") % path_info.path)

                paths.append(path)

    def check_versioning(self, version, release):
        try:
            int(release)
            pisi.version.make_version(version)
        except (ValueError, pisi.version.InvalidVersionError):
            raise Error(_("%s-%s is not a valid PiSi version format")
                        % (version, release))

    def check_build_dependencies(self):
        """check and try to install build dependencies, otherwise fail."""

        build_deps = self.spec.source.buildDependencies

        for package in self.spec.packages:
            build_deps.extend(package.buildDependencies)

        if not ctx.config.values.general.ignore_safety and \
                not ctx.get_option('ignore_safety'):
            if self.componentdb.has_component('system.devel'):
                build_deps_names = set([x.package for x in build_deps])
                devel_deps_names = set(self.componentdb.get_component('system.devel').packages)
                extra_names = devel_deps_names - build_deps_names
                extra_names = filter(lambda x: not self.installdb.has_package(x), extra_names)
                if extra_names:
                    ctx.ui.warning(_('Safety switch: following extra packages in system.devel will be installed: ') +
                               util.strlist(extra_names))
                    extra_deps = [dependency.Dependency(package=x) for x in extra_names]
                    build_deps.extend(extra_deps)
                else:
                    ctx.ui.info(_('Safety switch: system.devel is already installed'))
            else:
                ctx.ui.warning(_('Safety switch: the component system.devel cannot be found'))

        # find out the build dependencies that are not satisfied...
        dep_unsatis = []
        for dep in build_deps:
            if not dep.satisfied_by_installed():
                dep_unsatis.append(dep)

        if dep_unsatis:
            ctx.ui.info(_("Unsatisfied Build Dependencies:") + ' '
                        + util.strlist([str(x) for x in dep_unsatis]))

            def fail():
                raise Error(_('Cannot build package due to unsatisfied build dependencies'))

            if not ctx.config.get_option('ignore_dependency'):
                for dep in dep_unsatis:
                    if not dep.satisfied_by_repo():
                        raise Error(_('Build dependency %s cannot be satisfied') % str(dep))
                if ctx.ui.confirm(
                _('Do you want to install the unsatisfied build dependencies')):
                    ctx.ui.info(_('Installing build dependencies.'))
                    if not pisi.api.install([dep.package for dep in dep_unsatis], reinstall=True):
                        fail()
                else:
                    fail()
            else:
                ctx.ui.warning(_('Ignoring build dependencies.'))

    def check_patches(self):
        """check existence of patch files and their sizes."""

        files_dir = os.path.abspath(util.join_path(self.specdir,
                                                 ctx.const.files_dir))
        for patch in self.spec.source.patches:
            patchFile = util.join_path(files_dir, patch.filename)
            if not os.access(patchFile, os.F_OK):
                raise Error(_("Patch file is missing: %s\n") % patch.filename)
            if os.stat(patchFile).st_size == 0:
                ctx.ui.warning(_('Patch file is empty: %s') % patch.filename)

    def apply_patches(self):
        files_dir = os.path.abspath(util.join_path(self.specdir,
                                                 ctx.const.files_dir))

        for patch in self.spec.source.patches:
            patchFile = util.join_path(files_dir, patch.filename)
            relativePath = patch.filename
            reverseApply = patch.reverse and patch.reverse.lower() == "true"
            if patch.compressionType:
                patchFile = util.uncompress(patchFile,
                                            compressType=patch.compressionType,
                                            targetDir=ctx.config.tmp_dir())
                relativePath = relativePath.rsplit(".%s" % patch.compressionType, 1)[0]

            ctx.ui.action(_("* Applying patch: %s") % patch.filename)
            util.do_patch(self.pkg_src_dir(), patchFile,
                          level=patch.level,
                          name=relativePath,
                          reverse=reverseApply)
        return True

    def generate_static_package_object(self):
        ar_files = []
        for root, dirs, files in os.walk(self.pkg_install_dir()):
            for f in files:
                if f.endswith(ctx.const.ar_file_suffix) and util.is_ar_file(util.join_path(root, f)):
                    ar_files.append(util.join_path(root, f))

        if not len(ar_files):
            return None

        static_package_obj = pisi.specfile.Package()
        static_package_obj.name = self.spec.source.name + ctx.const.static_name_suffix
        # FIXME: find a better way to deal with the summary and description constants.
        static_package_obj.summary['en'] = u'Ar files for %s' % (self.spec.source.name)
        static_package_obj.description['en'] = u'Ar files for %s' % (self.spec.source.name)
        static_package_obj.partOf = self.spec.source.partOf
        for f in ar_files:
            static_package_obj.files.append(pisi.specfile.Path(path=f[len(self.pkg_install_dir()):], fileType="library"))

        # append all generated packages to dependencies
        for p in self.spec.packages:
            static_package_obj.packageDependencies.append(
                pisi.dependency.Dependency(package=p.name))

        return static_package_obj

    def generate_debug_package_object(self, package):
        debug_package_obj = pisi.specfile.Package()
        debug_package_obj.debug_package = True
        debug_package_obj.name = package.name + ctx.const.debug_name_suffix
        # FIXME: find a better way to deal with the summary and description constants.
        debug_package_obj.summary['en'] = u'Debug files for %s' % (package.name)
        debug_package_obj.description['en'] = u'Debug files for %s' % (package.name)
        debug_package_obj.partOf = package.partOf

        dependency = pisi.dependency.Dependency()
        dependency.package = package.name
        dependency.release = self.spec.history[0].release
        debug_package_obj.packageDependencies.append(dependency)

        for path_info in package.files:
            path = util.join_path(ctx.const.debug_files_suffix, path_info.path)
            debug_path_info = pisi.specfile.Path(path=path, fileType="debug")
            debug_package_obj.files.append(debug_path_info)

        return debug_package_obj

    def gen_metadata_xml(self, package):
        """Generate the metadata.xml file for build source.

        metadata.xml is composed of the information from specfile plus
        some additional information."""
        metadata = pisi.metadata.MetaData()
        metadata.from_spec(self.spec.source, package, self.spec.history)

        metadata.package.buildHost = ctx.config.values.build.build_host

        metadata.package.distribution = ctx.config.values.general.distribution
        metadata.package.distributionRelease = ctx.config.values.general.distribution_release
        metadata.package.architecture = ctx.config.values.general.architecture
        metadata.package.packageFormat = self.target_package_format

        size = 0
        for fileinfo in self.files.list:
            size += fileinfo.size

        metadata.package.installedSize = long(size)

        self.metadata = metadata

    def gen_files_xml(self, package):
        """Generates files.xml using the path definitions in specfile and
        the files produced by the build system."""
        files = pisi.files.Files()

        if package.debug_package:
            install_dir = self.pkg_debug_dir()
        else:
            install_dir = self.pkg_install_dir()

        # FIXME: We need to expand globs before trying to calculate hashes
        # Not on the fly like now.

        # we'll exclude collisions in get_file_hashes. Having a
        # collisions list is not wrong, we must just handle it :).
        collisions = check_path_collision(package, self.spec.packages)
        # FIXME: material collisions after expanding globs could be
        # reported as errors

        d = {}

        def add_path(path):
            # add the files under material path
            for fpath, fhash in util.get_file_hashes(path, collisions, install_dir):
                if ctx.get_option('create_static') \
                    and fpath.endswith(ctx.const.ar_file_suffix) \
                    and not package.name.endswith(ctx.const.static_name_suffix) \
                    and util.is_ar_file(fpath):
                    # if this is an ar file, and this package is not a static package,
                    # don't include this file into the package.
                    continue
                frpath = util.removepathprefix(install_dir, fpath)  # relative path
                ftype, permanent = get_file_type(frpath, package.files)
                fsize = long(util.dir_size(fpath))
                if not os.path.islink(fpath):
                    st = os.stat(fpath)
                else:
                    st = os.lstat(fpath)
                d[frpath] = pisi.files.FileInfo(path=frpath, type=ftype, permanent=permanent,
                                     size=fsize, hash=fhash, uid=str(st.st_uid), gid=str(st.st_gid),
                                     mode=oct(stat.S_IMODE(st.st_mode)))
                if stat.S_IMODE(st.st_mode) & stat.S_ISUID:
                    ctx.ui.warning(_("/%s has suid bit set") % frpath)

        for pinfo in package.files:
            wildcard_path = util.join_path(install_dir, pinfo.path)
            for path in glob.glob(wildcard_path):
                add_path(path)

        for (p, fileinfo) in d.iteritems():
            files.append(fileinfo)

        files_xml_path = util.join_path(self.pkg_dir(), ctx.const.files_xml)
        files.write(files_xml_path)
        self.files = files

    def file_actions(self):
        install_dir = self.pkg_install_dir()

        import magic
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()

        for root, dirs, files in os.walk(install_dir):
            for fn in files:
                filepath = util.join_path(root, fn)
                fileinfo = ms.file(filepath)
                strip_debug_action(filepath, fileinfo, install_dir, self.actionGlobals)
                exclude_special_files(filepath, fileinfo, self.actionGlobals)

        ms.close()

    def build_packages(self):
        """Build each package defined in PSPEC file. After this process there
        will be .pisi files hanging around, AS INTENDED ;)"""

        self.fetch_component()  # bug 856

        # Operations and filters for package files
        self.file_actions()

        if ctx.get_option('create_static'):
            obj = self.generate_static_package_object()
            if obj:
                self.spec.packages.append(obj)

        if ctx.config.values.build.generatedebug:
            debug_packages = []
            for package in self.spec.packages:
                if "noDebug" in package.buildFlags:
                    continue

                obj = self.generate_debug_package_object(package)
                if obj:
                    debug_packages.append(obj)

            if debug_packages:
                self.spec.packages.extend(debug_packages)

        install_dir = self.pkg_install_dir()

        # Store additional files
        c = os.getcwd()
        os.chdir(self.specdir)
        for package in self.spec.packages:
            for afile in package.additionalFiles:
                src = os.path.join(ctx.const.files_dir, afile.filename)
                dest = os.path.join(
                        install_dir + os.path.dirname(afile.target),
                        os.path.basename(afile.target))
                util.copy_file(src, dest)
                if afile.permission:
                    # mode is octal!
                    os.chmod(dest, int(afile.permission, 8))
                if afile.owner:
                    try:
                        os.chown(dest, pwd.getpwnam(afile.owner)[2], -1)
                    except KeyError:
                        ctx.ui.warning(_("No user named '%s' found "
                                         "on the system") % afile.owner)
                if afile.group:
                    try:
                        os.chown(dest, -1, grp.getgrnam(afile.group)[2])
                    except KeyError:
                        ctx.ui.warning(_("No group named '%s' found "
                                         "on the system") % afile.group)
        os.chdir(c)

        # Show the files those are not collected from the install dir
        abandoned_files = self.get_abandoned_files()
        if abandoned_files:
            ctx.ui.error(_("There are abandoned files "
                           "under the install dir (%s):") % install_dir)

            for f in abandoned_files:
                ctx.ui.info("    - %s" % f)

            raise AbandonedFilesException

        for package in self.spec.packages:
            # removing "farce" in specfile.py:SpecFile.override_tags
            # this block of code came here... SpecFile should never
            # ever ruin the generated PSPEC file. If build process
            # needs this, we should do it in here... (bug: #3773)
            if not package.summary:
                package.summary = self.spec.source.summary
            if not package.description:
                package.description = self.spec.source.description
            if not package.partOf:
                package.partOf = self.spec.source.partOf
            if not package.license:
                package.license = self.spec.source.license
            if not package.icon:
                package.icon = self.spec.source.icon

            self.gen_files_xml(package)

            if not self.files.list:
                if not package.debug_package:
                    ctx.ui.warning(_("Ignoring empty package %s") \
                                     % package.name)
                continue

            ctx.ui.action(_("Building package: %s") % package.name)

            self.gen_metadata_xml(package)

            self.metadata.write(util.join_path(self.pkg_dir(), ctx.const.metadata_xml))

            name = self.package_filename(self.metadata.package)

            outdir = ctx.get_option('output_dir')
            if outdir:
                name = util.join_path(outdir, name)

            name = os.path.normpath(name)

            if package.debug_package:
                self.new_debug_packages.append(name)
            else:
                self.new_packages.append(name)

            ctx.ui.info(_("Creating %s...") % name)

            pkg = pisi.package.Package(name, "w",
                                       format=self.target_package_format,
                                       tmp_dir=self.pkg_dir())

            # add comar files to package
            os.chdir(self.specdir)
            for pcomar in package.providesComar:
                fname = util.join_path(ctx.const.comar_dir,
                                     pcomar.script)
                pkg.add_to_package(fname)

            # add xmls and files
            os.chdir(self.pkg_dir())

            pkg.add_metadata_xml(ctx.const.metadata_xml)
            pkg.add_files_xml(ctx.const.files_xml)

            # Sort the files in-place according to their path for an ordered
            # tarfile layout which dramatically improves the compression
            # performance of lzma.
            pkg.files.list.sort(key=lambda x: x.path)

            for finfo in pkg.files.list:
                orgname = util.join_path("install", finfo.path)
                if package.debug_package:
                    orgname = util.join_path("debug", finfo.path)
                pkg.add_to_install(orgname, finfo.path)

            os.chdir(c)

            # FIXME Remove this hack
            pkg.metadata.package.debug_package = package.debug_package

            if "noDelta" not in package.buildFlags:
                delta_packages = self.build_delta_packages(pkg)
            else:
                delta_packages = []

            self.delta_map[name] = delta_packages

            pkg.close()

        self.set_state("buildpackages")

        if ctx.config.values.general.autoclean is True:
            ctx.ui.info(_("Cleaning build directory..."))
            util.clean_dir(self.pkg_dir())
        else:
            ctx.ui.info(_("Keeping build directory"))


        # reset environment variables after build.  this one is for
        # buildfarm actually. buildfarm re-inits pisi for each build
        # and left environment variables go directly into initial dict
        # making actionsapi.variables.exportFlags() useless...
        os.environ.clear()
        os.environ.update(ctx.config.environ)

    def search_old_packages_for_delta(self, release=None, max_count=0,
                                      search_paths=None):
        if search_paths is None:
            search_paths = (ctx.config.compiled_packages_dir(),
                            ctx.config.debug_packages_dir())

        if release is None:
            self.delta_history_search_paths.append((search_paths, max_count))
        else:
            self.delta_search_paths[release] = search_paths

    def build_delta_packages(self, package):

        def find_old_package(filename, search_paths):
            for package_dir in search_paths:
                path = util.join_path(package_dir, filename)
                if os.path.exists(path):
                    return path

        old_packages = {}

        for old_release, search_paths in self.delta_search_paths.items():
            if old_release in old_packages:
                continue

            update = None
            for update_tag in self.spec.history[1:]:
                if update_tag.release == old_release:
                    update = update_tag
                    break
            else:
                continue

            filename = self.package_filename(package.metadata.package, update)
            old_package = find_old_package(filename, search_paths)
            if old_package:
                old_packages[old_release] = old_package

        for search_paths, max_count in self.delta_history_search_paths:
            found_old_packages = {}
            for update in self.spec.history[1:]:
                if update.release in old_packages:
                    continue

                filename = self.package_filename(package.metadata.package,
                                                 update)
                old_package = find_old_package(filename, search_paths)
                if old_package:
                    found_old_packages[old_release] = old_package

                    if len(found_old_packages) == max_count:
                        break

            old_packages.update(found_old_packages)

        from pisi.operations.delta import create_delta_packages_from_obj
        return create_delta_packages_from_obj(old_packages.values(),
                                              package,
                                              self.specdir)


# build functions...

def build(pspec):
    if pspec.endswith('.xml'):
        pb = Builder(pspec)
    else:
        pb = Builder.from_name(pspec)
    try:
        pb.build()
    except ActionScriptException, e:
        ctx.ui.error("Action script error caught.")
        raise e
    finally:
        if ctx.ui.errors or ctx.ui.warnings:
            ctx.ui.warning(_("*** %d error(s), %d warning(s)") \
                            % (ctx.ui.errors, ctx.ui.warnings))
    return pb

order = {"none": 0,
         "fetch": 1,
         "unpack": 2,
         "setupaction": 3,
         "buildaction": 4,
         "installaction": 5,
         "buildpackages": 6}

def __buildState_fetch(pb):
    # fetch is the first state to run.
    pb.check_patches()
    pb.fetch_source_archives()

def __buildState_unpack(pb, last):
    if order[last] < order["fetch"]:
        __buildState_fetch(pb)
    pb.unpack_source_archives()

def __buildState_setupaction(pb, last):
    if order[last] < order["unpack"]:
        __buildState_unpack(pb, last)
    pb.run_setup_action()

def __buildState_buildaction(pb, last):

    if order[last] < order["setupaction"]:
        __buildState_setupaction(pb, last)
    pb.run_build_action()

def __buildState_checkaction(pb, last):

    if order[last] < order["buildaction"]:
        __buildState_buildaction(pb, last)
    pb.run_check_action()

def __buildState_installaction(pb, last):

    if order[last] < order["buildaction"]:
        __buildState_buildaction(pb, last)
    pb.run_install_action()

def __buildState_buildpackages(pb):

    for build_type in pb.build_types:
        pb.set_build_type(build_type)
        last = pb.get_state() or "none"

        if order[last] < order["installaction"]:
            __buildState_installaction(pb, last)

    pb.build_packages()

def build_until(pspec, state):
    if pspec.endswith('.xml'):
        pb = Builder(pspec)
    else:
        pb = Builder.from_name(pspec)

    pb.compile_comar_script()

    if state == "fetch":
        __buildState_fetch(pb)
        return

    # from now on build dependencies are needed
    pb.check_build_dependencies()

    if state == "package":
        __buildState_buildpackages(pb)
        return

    for build_type in pb.build_types:
        pb.set_build_type(build_type)
        last = pb.get_state() or "none"

        __build_until(pb, state, last)


def __build_until(pb, state, last):
    ctx.ui.info("Last state was %s" % last)

    if state == "unpack":
        __buildState_unpack(pb, last)
        return

    if state == "setup":
        __buildState_setupaction(pb, last)
        return

    if state == "build":
        __buildState_buildaction(pb, last)
        return

    if state == "check":
        __buildState_checkaction(pb, last)
        return

    if state == "install":
        __buildState_installaction(pb, last)
