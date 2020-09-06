# -*- coding: utf-8 -*-
#
# Main fork Pisi: Copyright (C) 2005 - 2011, Tubitak/UEKAE
#
# Copyright (C) 2016 - 2020, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

"""package building code"""

# Standart Python Modules
import os
import re
import grp
import pwd
import glob
import stat
import fnmatch

# Inary Modules
import inary.db
import inary.uri
import inary.file
import inary.errors
import inary.archive
import inary.fetcher
import inary.package
import inary.util as util
import inary.context as ctx
import inary.process as process
import inary.data.files as Files
import inary.actionsapi.variables
import inary.data.metadata as Metadata
import inary.data.specfile as Specfile
import inary.data.component as Component
import inary.analyzer.dependency as dependency

# Gettext Library
import gettext

__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext


class Error(inary.errors.Error):
    pass


class ActionScriptException(Error):
    pass


class AbandonedFilesException(inary.errors.Error):
    pass


class ExcludedArchitectureException(Error):
    pass


# Helper Functions
def get_file_type(path, pinfo_list):
    """Return the file type of a path according to the given PathInfo
    list"""

    path = "/{}".format(re.sub("/+", "/", path))
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
                    ctx.ui.debug(
                        _('Path \"{}\" belongs in multiple packages.').format(
                            path.path))
    return collisions


def exclude_special_files(filepath, fileinfo, keeplist):
    patterns = {"libtool": "libtool library file",
                "python": "python.*byte-compiled",
                "perl": "Perl POD document text"}

    if "libtool" in keeplist:
        # Some upstream sources have buggy libtool and ltmain.sh with them,
        # which causes wrong path entries in *.la files. And these wrong path
        # entries sometimes triggers compile-time errors or linkage problems.
        # Instead of patching all these buggy sources and maintain these
        # patches, INARY removes wrong paths...
        if re.match(patterns["libtool"], fileinfo) and \
                not os.path.islink(filepath):
            ladata = open(filepath).read()
            new_ladata = re.sub(
                r"-L{}/\S*".format(ctx.config.tmp_dir()), "", ladata)
            new_ladata = re.sub("{}/\S*/install/".format(ctx.config.tmp_dir()), "/",
                                new_ladata)
            if new_ladata != ladata:
                open(filepath, "w").write(new_ladata)
    for name, pattern in list(patterns.items()):
        if name in keeplist:
            continue

        if fileinfo is None:
            ctx.ui.warning(
                _("Removing special file skipped for: \"{}\"").format(filepath))
            return
        elif re.match(pattern, fileinfo):
            ctx.ui.warning(
                _("Removing special \"{0}\" file: \"{1}\"").format(
                    name, filepath))
            os.unlink(filepath)
            # Remove dir if it becomes empty (Bug #11588)
            util.rmdirs(os.path.dirname(filepath))


def strip_debug_action(filepath, fileinfo, install_dir, excludelist):

    # real path in .inary package
    path = '/' + util.removepathprefix(install_dir, filepath)

    if path.startswith(excludelist):
        return
    outputpath = util.join_path(os.path.dirname(install_dir),
                                ctx.const.debug_dir_suffix,
                                ctx.const.debug_files_suffix,
                                path)
    if util.strip_file(filepath, fileinfo, outputpath):
        ctx.ui.info("{0} [{1}]".format(path, "stripped"), verbose=True)


class Builder:
    """Provides the package build and creation routines"""

    # FIXME: this class and every other class must use URLs as paths!

    @staticmethod
    def from_name(name):
        repodb = inary.db.repodb.RepoDB()
        sourcedb = inary.db.sourcedb.SourceDB()
        # download package and return an installer object
        # find package in repository
        sf, reponame = sourcedb.get_spec_repo(name)
        src = sf.source
        if src:

            src_uri = inary.uri.URI(src.sourceURI)
            if src_uri.is_absolute_path():
                src_path = str(src_uri)
            else:
                repo = repodb.get_repo(reponame)
                # FIXME: don't use dirname to work on URLs
                src_path = os.path.join(
                    os.path.dirname(repo.indexuri.get_uri()),
                    str(src_uri.path()))

            ctx.ui.info(_("Source URI: {}").format(src_path), verbose=True)

            return Builder(src_path)
        else:
            raise Error(
                _("Source \"{}\" not found in any active repository.").format(name))

    def __init__(self, specuri):

        self.componentdb = inary.db.componentdb.ComponentDB()
        self.installdb = inary.db.installdb.InstallDB()

        # process args
        if not isinstance(specuri, inary.uri.URI):
            specuri = inary.uri.URI(specuri)

        # read spec file, we'll need it :)
        self.set_spec_file(specuri)

        if specuri.is_remote_file():
            self.specdir = self.fetch_files()
        else:
            self.specdir = os.path.dirname(self.specuri.get_uri())

        # Don't wait until creating .inary file for complaining about versioning
        # scheme errors
        self.package_rfp = None
        if self.spec.source.rfp:
            ctx.ui.info(util.colorize(_("[ !!! ] Building RFP for {}").format(self.spec.source.rfp),
                                      color="purple"))
            if ctx.ui.confirm(
                    _("Would you like to compile this RFP package?")):
                self.package_rfp = self.spec.source.rfp
            else:
                raise Error(_("Didn't permit build RFP package."))

        self.check_versioning(self.spec.getSourceVersion(),
                              self.spec.getSourceRelease())

        # Check package format
        self.target_package_format = ctx.get_option("package_format") \
            or inary.package.Package.default_format

        self.read_translations(self.specdir)

        self.sourceArchives = inary.archive.SourceArchives(self.spec)

        self.build_types = self.get_build_types()

        # Use an empty string for the default build
        self.set_build_type("")

        self.check_paths()

        self.actionGlobals = None
        self.actionScript = ""

        self.delta_history_search_paths = []
        self.delta_search_paths = {}

        self.new_packages = []
        self.new_debug_packages = []

        self.delta_map = {}

        self.has_ccache = False
        self.has_icecream = False
        self.variable_buffer = {}

    def set_spec_file(self, specuri):
        if not specuri.is_remote_file():
            # FIXME: doesn't work for file://
            specuri = inary.uri.URI(os.path.realpath(specuri.get_uri()))
        self.specuri = specuri
        spec = Specfile.SpecFile()
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

        if self.package_rfp:
            package_extension = ".rfp" + ctx.const.package_suffix
        else:
            package_extension = ctx.const.package_suffix
        if with_extension:
            fn += package_extension

        return fn

    # directory accessor functions

    # pkg_x_dir: per package directory for storing info type x

    def pkg_dir(self):
        """package build directory"""
        packageDir = self.spec.source.name + '-' + \
            self.spec.getSourceVersion() + '-' + \
            self.spec.getSourceRelease()
        return util.join_path(ctx.config.dest_dir(),
                              ctx.config.tmp_dir(),
                              packageDir)

    def pkg_work_dir(self):
        suffix = "-{}".format(self.build_type) if self.build_type else ""
        return self.pkg_dir() + ctx.const.work_dir_suffix + suffix

    def pkg_debug_dir(self):
        return self.pkg_dir() + ctx.const.debug_dir_suffix

    def pkg_install_dir(self):
        return self.pkg_dir() + ctx.const.install_dir_suffix

    def set_state(self, state):
        stateFile = util.join_path(self.pkg_work_dir(), "inaryBuildState")
        open(stateFile, "w").write(state)

    def get_state(self):
        stateFile = util.join_path(self.pkg_work_dir(), "inaryBuildState")
        if not os.path.exists(stateFile):  # no state
            return None
        return open(stateFile).read()

    def build(self):
        """Build the package in one shot."""
        architecture = ctx.config.values.general.architecture
        if architecture in self.spec.source.excludeArch:
            raise ExcludedArchitectureException(
                _("pspec.xml avoids this package from building for \"{}\"").format(
                    architecture))

        ctx.ui.status(_("Building source package: \"{}\"").format(
            self.spec.source.name))
        # check if all patch files exists, if there are missing no need
        # to unpack!
        self.check_patches()

        self.check_build_dependencies()
        self.fetch_component()
        self.fetch_source_archives()

        util.clean_dir(self.pkg_install_dir())
        if not os.path.exists(self.pkg_install_dir()):
            util.ensure_dirs(self.pkg_install_dir())

        for build_type in self.build_types:
            self.set_build_type(build_type)
            self.unpack_source_archives()

            if self.has_ccache:
                ctx.ui.info(_("ccache detected..."))
            if self.has_icecream:
                ctx.ui.info(_("IceCream detected. Make sure your daemon "
                              "is up and running..."))
        for build_type in self.build_types:
            self.set_build_type(build_type)
            self.run_setup_action()
        for build_type in self.build_types:
            self.set_build_type(build_type)
            self.run_build_action()
        for build_type in self.build_types:
            self.set_build_type(build_type)
            if ctx.get_option('debug') and not ctx.get_option('ignore_check'):
                self.run_check_action()
        for build_type in self.build_types:
            self.set_build_type(build_type)
            self.run_install_action()

        # after all, we are ready to build/prepare the packages
        self.build_packages()

    def get_build_types(self):
        ignored_build_types = \
            ctx.config.values.build.ignored_build_types.split(",")
        build_types = []
        packages = []

        for package in self.spec.packages:
            if package.buildType:
                if package.buildType in ignored_build_types:
                    continue

                if package.buildType not in build_types:
                    build_types.append(package.buildType)

            packages.append(package)

        self.spec.packages = packages
        build_types.append("")
        return build_types

    def set_build_type(self, build_type):
        if build_type:
            ctx.ui.action(
                _("Rebuilding source for build type: {}").format(build_type))

        self.build_type = build_type

    def set_environment_vars(self):
        """Sets the environment variables for actions API to use"""

        # Each time a builder is created we must reset
        # environment. See bug #2575

        os.environ.clear()

        # inary.actionsapi.variables.initVariables()

        env = {"PKG_DIR": self.pkg_dir(),
               "WORK_DIR": self.pkg_src_dir(),
               "SRCDIR": self.pkg_work_dir(),
               "HOME": self.pkg_work_dir(),
               "INSTALL_DIR": self.pkg_install_dir(),
               "INARY_BUILD_TYPE": self.build_type,
               "SRC_NAME": self.spec.source.name,
               "SRC_VERSION": self.spec.getSourceVersion(),
               "SRC_RELEASE": self.spec.getSourceRelease(),
               "PATH": "/bin:/usr/bin:/sbin:/usr/sbin",
               "PYTHONDONTWRITEBYTECODE": '1'}
        if self.build_type == "emul32":
            env["CC"] = "{} -m32".format(util.getenv("CC"))
            env["CXX"] = "{} -m32".format(util.getenv("CXX"))
            env["CFLAGS"] = util.getenv("CFLAGS").replace("-fPIC", "")
            env["CXXFLAGS"] = util.getenv("CXXFLAGS").replace("-fPIC", "")
            env["PKG_CONFIG_PATH"] = "/usr/lib32/pkgconfig"
        if self.build_type == "clang":
            env['CC'] = "clang"
            env['CXX'] = "clang++"
        if self.build_type == "clang32":
            env['CC'] = "clang -m32"
            env['CXX'] = "clang++ -m32"
        os.environ.update(env)

        # First check icecream, if not found use ccache
        # TODO: Add support for using both of them
        if ctx.config.values.build.buildhelper == "icecream":
            if os.path.exists("/opt/icecream/bin/gcc"):
                self.has_icecream = True
                os.environ["PATH"] = "/opt/icecream/bin:%(PATH)s" % os.environ

        elif ctx.config.values.build.buildhelper == "ccache":
            if os.path.exists("/usr/lib/ccache/bin/gcc"):
                self.has_ccache = True

                os.environ["PATH"] = "/usr/lib/ccache/bin:%(PATH)s" % os.environ
                # Force ccache to use /root/.ccache instead of $HOME/.ccache
                # as $HOME can be modified through actions.py
                os.environ["CCACHE_DIR"] = "/tmp/.ccache"

    def fetch_files(self):
        self.specdiruri = os.path.dirname(self.specuri.get_uri())
        pkgname = os.path.basename(self.specdiruri)
        self.destdir = util.join_path(ctx.config.tmp_dir(), pkgname)
        # self.location = os.path.dirname(self.url.uri)

        self.fetch_actionsfile()
        self.check_build_dependencies()
        self.fetch_translationsfile()
        self.fetch_patches()
        self.fetch_additionalFiles()
        self.fetch_postops()

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
        except inary.fetcher.FetchError:
            # translations.xml is not mandatory for INARY
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

    def fetch_postops(self):
        for postops in ctx.const.postops:
            postops_script = util.join_path(self.specdiruri, postops)
            if util.check_file(postops_script, noerr=True):
                self.download(postops_script, util.join_path(self.specdir))
                ctx.ui.info(_("PostOps Script Fetched."))

    @staticmethod
    def download(uri, transferdir):
        # fix auth info and download
        uri = inary.file.File.make_uri(uri)
        inary.file.File.download(uri, transferdir)

    def fetch_component(self):
        if self.spec.source.partOf:
            return

        diruri = util.parenturi(self.specuri.get_uri())
        parentdir = util.parenturi(diruri)
        url = util.join_path(parentdir, 'component.xml')
        progress = ctx.ui.Progress
        if inary.uri.URI(url).is_remote_file():
            try:
                inary.fetcher.fetch_url(url, self.pkg_work_dir(), progress)
            except inary.fetcher.FetchError:
                ctx.ui.warning(_("Cannot find component.xml for \"{}\" in remote "
                                 "directory, Source is now part of "
                                 "unknown component.").format(self.spec.source.name))
                self.spec.source.partOf = 'unknown'
                return
            path = util.join_path(self.pkg_work_dir(), 'component.xml')
        else:
            if not os.path.exists(url):
                ctx.ui.warning(_("Cannot find component.xml for \"{}\" in upper "
                                 "directory, Source is now part of "
                                 "unknown component.").format(self.spec.source.name))
                self.spec.source.partOf = 'unknown'
                return
            path = url
        comp = Component.CompatComponent()
        comp.read(path)
        self.spec.source.partOf = comp.name

    def fetch_source_archives(self):
        ctx.ui.status(_("Building source package: \"{}\" [ Fetching Step ]").format(self.spec.source.name),
                      push_screen=False)
        self.sourceArchives.fetch()

    def unpack_source_archives(self):
        ctx.ui.status(_("Building source package: \"{}\" [ Unpacking Step ]").format(self.spec.source.name),
                      push_screen=False)
        ctx.ui.action(
            util.colorize(
                ">>> ",
                'purple') +
            _("Unpacking archive(s)..."))
        self.sourceArchives.unpack(self.pkg_work_dir())

        # Grab AdditionalFiles
        self.copy_additional_source_files()

        # apply the patches and prepare a source directory for build.
        if self.apply_patches():
            ctx.ui.info(_(" -> unpacked ({})").format(self.pkg_work_dir()))
            self.set_state("unpack")

    def run_setup_action(self):
        #  Run configure, build and install phase
        ctx.ui.status(_("Building source package: \"{}\" [ SetupAction Step ]").format(self.spec.source.name),
                      push_screen=False)
        ctx.ui.action(
            util.colorize(
                ">>> ",
                'yellow') +
            _("Setting up source..."))
        if self.run_action_function(ctx.const.setup_func):
            self.set_state("setupaction")

    def run_build_action(self):
        ctx.ui.status(_("Building source package: \"{}\" [ BuildAction Step ]").format(self.spec.source.name),
                      push_screen=False)
        ctx.ui.action(util.colorize(">>> ", 'green') + _("Building source..."))
        if self.run_action_function(ctx.const.build_func):
            self.set_state("buildaction")

    def run_check_action(self):
        ctx.ui.status(_("Building source package: \"{}\" [ CheckAction Step ]").format(self.spec.source.name),
                      push_screen=False)
        ctx.ui.action(util.colorize(">>> ", 'blue') + _("Testing package..."))
        self.run_action_function(ctx.const.check_func)

    def run_install_action(self):
        ctx.ui.status(_("Building source package: \"{}\" [ InstallAction Step ]").format(self.spec.source.name),
                      push_screen=False)
        ctx.ui.action(util.colorize(">>> ", 'cyan') + _("Installing..."))
        install_dir = self.pkg_install_dir()

        # install function is mandatory!
        if self.run_action_function(ctx.const.install_func, True):
            self.set_state("installaction")

    def get_abandoned_files(self):
        # return the files those are not collected from the install dir

        install_dir = self.pkg_install_dir()
        abandoned_files = []
        all_paths_in_packages = []
        skip_paths = []

        for package in self.spec.packages:
            for path in package.files:
                path = util.join_path(install_dir, path.path)
                all_paths_in_packages.append(path)

        def is_included(path1, path2):
            """Return True if path2 includes path1"""
            return path1 == path2 \
                or fnmatch.fnmatch(path1, path2) \
                or (not os.path.isfile(path2) and fnmatch.fnmatch(path1, util.join_path(path2, "*")))

        for root, dirs, files in os.walk(install_dir):
            if not dirs and not files:
                for _path in all_paths_in_packages:
                    if is_included(root, _path):
                        break
                else:
                    abandoned_files.append(root)

            if root in all_paths_in_packages:
                skip_paths.append(root)
                continue

            skip = False
            for skip_path in skip_paths:
                if root.startswith(skip_path):
                    skip = True
                    break
            if skip:
                continue

            for file_ in files:
                fpath = util.join_path(root, file_)
                for _path in all_paths_in_packages:
                    if is_included(fpath, _path):
                        if os.path.isfile(_path):
                            all_paths_in_packages.pop(
                                all_paths_in_packages.index(_path))
                        break
                else:
                    abandoned_files.append(fpath)

        len_install_dir = len(install_dir)
        return [x[len_install_dir:] for x in abandoned_files]

    def copy_additional_source_files(self):
        # store additional files
        for afile in self.spec.source.additionalFiles:
            src = os.path.join(
                self.specdir,
                ctx.const.files_dir,
                afile.filename)
            dest = os.path.join(self.pkg_src_dir(), afile.target)
            util.copy_file(src, dest)
            if afile.permission:
                # mode is octal!
                os.chmod(dest, int(afile.permission, 8))

    def get_action_variable(self, name, default):
        if name in self.variable_buffer.keys():
            return self.variable_buffer[name]
        else:
            (ret, out, err) = util.run_batch(
                'python3 -c \'import sys\nsys.path.append("{1}")\nimport actions\nsys.stdout.write(actions.{0})\''.format(name, os.getcwd()))
            if ret == 0:
                self.variable_buffer[name] = out
                return out
            else:
                return default

    def pkg_src_dir(self):
        """Returns the real path of WorkDir for an unpacked archive."""

        dirname = self.get_action_variable("WorkDir", "")
        if dirname == "":
            dirname = self.spec.source.name + "-" + self.spec.getSourceVersion()
        src_dir = util.join_path(self.pkg_work_dir(), dirname)
        if not os.path.exists(src_dir):
            util.ensure_dirs(src_dir)

            # For binary types, WorkDir is usually "."
        archive = self.spec.source.archive[0]
        if archive.type == "binary":
            return self.pkg_work_dir()
        else:
            return src_dir

    def run_action_function(self, func, mandatory=False):
        """Calls the corresponding function in actions.py.

        If mandatory parameter is True, and function is not present in
        actionLocals inary.build.Error will be raised."""
        # we'll need our working directory after actionscript
        # finished its work in the archive source directory.
        curDir = os.getcwd()
        src_dir = self.pkg_src_dir()
        self.set_environment_vars()
        os.environ['WORK_DIR'] = src_dir
        os.environ['CURDIR'] = curDir
        os.environ['SRCDIR'] = self.pkg_work_dir()
        os.environ['OPERATION'] = func
        if os.path.exists(src_dir):
            os.chdir(src_dir)
        else:
            raise Error(
                _("ERROR: WorkDir ({}) does not exist\n").format(src_dir))

        if os.system('python3 -c \'import sys\nsys.path.append("{1}")\nimport actions\nif(hasattr(actions,"{0}")): actions.{0}()\''.format(func, curDir)):
            raise Error(
                _("unable to call function from actions: \'{}\'").format(func))
        os.chdir(curDir)
        return True

    def check_paths(self):
        paths = []

        for package in self.spec.packages:
            for path_info in package.files:
                path = os.path.normpath(path_info.path)

                if not path.startswith("/"):
                    raise Error(_("Source package '{0}' defines a relative 'Path' element: "
                                  "{1}").format(self.spec.source.name, path_info.path))

                if path in paths:
                    raise Error(_("Source package '{0}' defines multiple 'Path' tags "
                                  "for {1}").format(self.spec.source.name, path_info.path))

                paths.append(path)

    @staticmethod
    def check_versioning(version, release):
        try:
            int(release)
            inary.version.make_version(version)
        except (ValueError, inary.version.InvalidVersionError):
            raise Error(
                _("{0}-{1} is not a valid INARY version format").format(version, release))

    def check_build_dependencies(self):
        """check and try to install build dependencies, otherwise fail."""

        build_deps = self.spec.source.buildDependencies

        for package in self.spec.packages:
            build_deps.extend(package.buildDependencies)

        if not ctx.config.values.general.ignore_safety and \
                not ctx.get_option('ignore_safety'):
            if self.componentdb.has_component('system.devel'):
                build_deps_names = set([x.package for x in build_deps])
                devel_deps_names = set(
                    self.componentdb.get_component('system.devel').packages)
                extra_names = devel_deps_names - build_deps_names
                extra_names = [
                    x for x in extra_names if not self.installdb.has_package(x)]
                if extra_names:
                    ctx.ui.warning(_('Safety switch: following extra packages in system.devel will be installed: ') +
                                   util.strlist(extra_names))
                    extra_deps = [
                        dependency.Dependency(
                            package=x) for x in extra_names]
                    build_deps.extend(extra_deps)
            else:
                ctx.ui.warning(
                    _('Safety switch: the component system.devel cannot be found.'))

        # find out the build dependencies that are not satisfied...
        dep_unsatis = []
        for dep in build_deps:
            if not dep.satisfied_by_installed():
                dep_unsatis.append(dep)

        if dep_unsatis:
            ctx.ui.info(_("Unsatisfied Build Dependencies:") + ' '
                        + util.strlist([str(x) for x in dep_unsatis]))

            def fail():
                raise Error(
                    _('Cannot build package due to unsatisfied build dependencies.'))

            if not ctx.config.get_option('ignore_dependency'):
                for dep in dep_unsatis:
                    if not dep.satisfied_by_repo():
                        raise Error(
                            _('Build dependency \"{}\" cannot be satisfied.').format(
                                str(dep)))
                if ctx.ui.confirm(
                        _('Would you like to install the unsatisfied build dependencies?')):
                    ctx.ui.info(_('Installing build dependencies.'))
                    if not inary.operations.install.install(
                            [dep.package for dep in dep_unsatis], reinstall=False):
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
                raise Error(
                    _("Patch file is missing: \"{}\"\n").format(
                        patch.filename))
            if os.stat(patchFile).st_size == 0:
                ctx.ui.warning(
                    _('Patch file is empty: \"{}\"').format(
                        patch.filename))

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
                relativePath = relativePath.rsplit(
                    ".{}".format(patch.compressionType, 1))[0]

            ctx.ui.action(_("Applying patch: {}").format(patch.filename))
            util.do_patch(self.pkg_src_dir(), patchFile,
                          level=patch.level,
                          name=relativePath,
                          reverse=reverseApply)
        return True

    def generate_static_package_object(self):
        ar_files = []
        for root, dirs, files in os.walk(self.pkg_install_dir()):
            for f in files:
                if f.endswith(ctx.const.ar_file_suffix) and util.is_ar_file(
                        util.join_path(root, f)):
                    ar_files.append(util.join_path(root, f))

        if not len(ar_files):
            return None

        static_package_obj = Specfile.Package()
        static_package_obj.name = self.spec.source.name + ctx.const.static_name_suffix
        # FIXME: find a better way to deal with the summary and description
        # constants.
        static_package_obj.summary['en'] = 'Ar files for {}'.format(
            self.spec.source.name)
        static_package_obj.description['en'] = 'Ar files for {}'.format(
            self.spec.source.name)
        static_package_obj.partOf = "static"
        for f in ar_files:
            static_package_obj.files.append(Specfile.Path(
                path=f[len(self.pkg_install_dir()):], fileType="library"))

        # append all generated packages to dependencies
        for p in self.spec.packages:
            static_package_obj.packageDependencies.append(
                inary.analyzer.dependency.Dependency(package=p.name))

        return static_package_obj

    def generate_debug_package_object(self, package):
        debug_package_obj = Specfile.Package()
        debug_package_obj.debug_package = True
        debug_package_obj.name = package.name + ctx.const.debug_name_suffix
        # FIXME: find a better way to deal with the summary and description
        # constants.
        debug_package_obj.summary['en'] = 'Debug files for {}'.format(
            package.name)
        debug_package_obj.description['en'] = 'Debug files for {}'.format(
            package.name)
        debug_package_obj.partOf = "dbginfo"

        dependency = inary.analyzer.dependency.Dependency()
        dependency.package = package.name
        dependency.release = self.spec.history[0].release
        debug_package_obj.packageDependencies.append(dependency)

        for path_info in package.files:
            path = util.join_path(ctx.const.debug_files_suffix, path_info.path)
            debug_path_info = Specfile.Path(path=path, fileType="debug")
            debug_package_obj.files.append(debug_path_info)

        return debug_package_obj

    def gen_metadata_xml(self, package):
        """Generate the metadata.xml file for build source.

        metadata.xml is composed of the information from specfile plus
        some additional information."""
        metadata = Metadata.MetaData()
        metadata.from_spec(self.spec.source, package, self.spec.history)

        metadata.package.buildHost = ctx.config.values.build.build_host

        metadata.package.distribution = ctx.config.values.general.distribution
        metadata.package.distributionRelease = ctx.config.values.general.distribution_release
        metadata.package.architecture = ctx.config.values.general.architecture
        metadata.package.packageFormat = self.target_package_format

        size = 0
        for fileinfo in self.files.list:
            size += fileinfo.size

        metadata.package.installedSize = int(size)

        self.metadata = metadata
        if int(size) == 0:
            return False
        return True

    def gen_files_xml(self, package):
        """Generates files.xml using the path definitions in specfile and
        the files produced by the build system."""

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

        # Use a dict to avoid duplicate entries in files.xml.
        d = {}

        def add_path(path):
            # add the files under material path
            for fpath, fhash in util.get_file_hashes(
                    path, collisions, install_dir):
                if ctx.get_option('create_static') \
                        and fpath.endswith(ctx.const.ar_file_suffix) \
                        and not package.name.endswith(ctx.const.static_name_suffix) \
                        and util.is_ar_file(fpath):
                    # if this is an ar file, and this package is not a static package,
                    # don't include this file into the package.
                    continue
                frpath = util.removepathprefix(
                    install_dir, fpath)  # relative path
                ftype, permanent = get_file_type(frpath, package.files)
                fsize = int(util.dir_size(fpath))
                if not os.path.islink(fpath):
                    st = os.stat(fpath)
                else:
                    st = os.lstat(fpath)
                _uid = str(st.st_uid)
                _gid = str(st.st_gid)

                for afile in package.additionalFiles:
                    # FIXME: Better way?
                    if frpath == util.removepathprefix("/", afile.target):
                        # This is an additional file, uid and gid will change
                        if afile.owner is None:
                            afile.owner = "root"
                        if afile.group is None:
                            afile.group = "root"

                        try:
                            _uid = str(pwd.getpwnam(afile.owner)[2])
                        except KeyError:
                            ctx.ui.warning(_("No user named '{}' found "
                                             "on the system").format(afile.owner))
                        try:
                            _gid = str(grp.getgrnam(afile.group)[2])
                        except KeyError:
                            ctx.ui.warning(_("No group named '{}' found "
                                             "on the system").format(afile.group))
                        break
                d[frpath] = Files.FileInfo(path=frpath, type=ftype, permanent=permanent,
                                           size=fsize, hash=fhash, uid=_uid, gid=_gid,
                                           mode=oct(stat.S_IMODE(st.st_mode)))

                if stat.S_IMODE(st.st_mode) & stat.S_ISUID:
                    ctx.ui.warning(_("/{} has suid bit set").format(frpath))

        for pinfo in package.files:
            wildcard_path = util.join_path(install_dir, pinfo.path)
            for path in glob.glob(wildcard_path):
                add_path(path)

        files = Files.Files()
        for fileinfo in d.values():
            files.append(fileinfo)

        files_xml_path = util.join_path(self.pkg_dir(), ctx.const.files_xml)
        files.write(files_xml_path)
        self.files = files

    def file_actions(self):
        install_dir = self.pkg_install_dir()
        witcher = None  # Who makes magic? ;)
        try:
            witcher = __import__("magic").detect_from_filename
        except ImportError:
            ctx.ui.warning(_("Module \"magic\" cannot found. Falling back with \"file\" command. \
It is dangerous. So, if you wanna create stable packages, please fix \
this issue in your workplace. Probably installing \"python3-filemagic\" \
package might be a good solution."))

        self.nostrip = tuple(self.get_action_variable("NoStrip", []))
        self.keepspecial = self.get_action_variable("KeepSpecial", [])
        for root, dirs, files in os.walk(install_dir):
            for fn in files:
                filepath = util.join_path(root, fn)
                if witcher:
                    try:
                        fileinfo = witcher(filepath).name
                    except ValueError:
                        ctx.ui.warning(
                            _("File \"{}\" might be a broken symlink. Check it before publishing package.".format(filepath)))
                        fileinfo = "broken symlink"
                    ctx.ui.info(
                        _("\'magic\' return of \"{0}\" is \"{1}\"").format(
                            filepath, fileinfo), verbose=True)
                else:
                    result = util.run_batch(
                        "file {}".format(filepath), ui_debug=False)
                    if result[0]:
                        ctx.ui.error(_("\'file\' command failed with return code {0} for file: \"{1}\"").format(result[0], filepath) +
                                     _("Output:\n{}").format(result[1]))

                    fileinfo = str(result[1])
                    ctx.ui.info(
                        _("\'file\' command return is \"{}\"").format(
                            result[1]), verbose=True)

                strip_debug_action(
                    filepath,
                    fileinfo,
                    install_dir, self.nostrip)
                exclude_special_files(filepath, fileinfo, self.keepspecial)

    def build_packages(self):
        """Build each package defined in PSPEC file. After this process there
        will be .inary files hanging around, AS INTENDED ;)"""

        ctx.ui.status(
            _("Compiled source building package files generating for source: \"{}\"").format(
                self.spec.source.name), push_screen=True)

        doc_ptrn = re.compile(ctx.const.doc_package_end)

        self.fetch_component()  # bug 856
        ctx.ui.status(
            _("Running file actions: \"{}\"").format(
                self.spec.source.name), push_screen=True)

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

                # FIXME: Check that chmodding is safe for non-root builds
                if afile.permission:
                    # mode is octal!
                    os.chmod(dest, int(afile.permission, 8))

        os.chdir(c)

        # Show the files those are not collected from the install dir
        abandoned_files = self.get_abandoned_files()
        if abandoned_files:
            ctx.ui.error(_("There are abandoned files "
                           "under the install dir ({}):").format(install_dir))

            for f in abandoned_files:
                ctx.ui.info("    - {}".format(f))

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
                if package.name.endswith(ctx.const.devel_package_end):
                    if self.spec.source.partOf in ctx.const.assign_to_system_devel:
                        package.partOf = ctx.const.system_devel_component
                    else:
                        package.partOf = ctx.const.devels_component
                elif re.search(doc_ptrn, package.name):
                    package.partOf = ctx.const.docs_component
                else:
                    package.partOf = self.spec.source.partOf
            if not package.license:
                package.license = self.spec.source.license
            if not package.icon:
                package.icon = self.spec.source.icon

            self.gen_files_xml(package)

            if not self.files.list:
                if not package.debug_package:
                    ctx.ui.warning(
                        _("Ignoring empty package: \"{}\"").format(
                            package.name))
                continue

            if not self.gen_metadata_xml(package):
                ctx.ui.warning(
                    _("Ignoring empty package: \"{}\"").format(
                        package.name))
                continue

            ctx.ui.status(
                _("Building package: \"{}\"").format(
                    package.name), push_screen=True)

            name = self.package_filename(self.metadata.package)

            outdir = ctx.get_option('output_dir')
            if outdir:
                name = util.join_path(outdir, name)

            name = os.path.normpath(name)

            if package.debug_package:
                self.new_debug_packages.append(name)
            else:
                self.new_packages.append(name)

            ctx.ui.info(_("Creating \"{}\"...").format(name))

            pkg = inary.package.Package(name, "w",
                                        format=self.target_package_format,
                                        tmp_dir=self.pkg_dir())

            # add postops files to package
            os.chdir(self.specdir)
            for postops in ctx.const.postops:
                if util.check_file(postops, noerr=True) and (
                        'postOps' in self.metadata.package.isA):
                    pkg.add_to_package(postops)

            # add xmls and files
            os.chdir(self.pkg_dir())
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

            if self.target_package_format == "1.3":
                archive_format = ".tar.gz"
            elif self.target_package_format == "1.2":
                archive_format = ".tar.xz"
            elif self.target_package_format == "1.1":
                archive_format = ".tar.lzma"
            else:
                # "1.0" format does not have an archive
                archive_format = ".tar"

            self.metadata.package.installTarHash = util.sha1_file(
                "{0}/install{1}".format(self.pkg_dir(), archive_format))
            self.metadata.write(
                util.join_path(
                    self.pkg_dir(),
                    ctx.const.metadata_xml))
            pkg.add_metadata_xml(ctx.const.metadata_xml)

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
        # buildfarm actually. buildfarm re-inits inary for each build
        # and left environment variables go directly into initial dict
        # making actionsapi.variables.exportFlags() useless...
        os.environ.clear()
        os.environ.update(ctx.config.environ)

    def search_old_packages_for_delta(self, release=None, max_count=0,
                                      search_paths=None):
        if search_paths is None:
            search_paths = (ctx.config.compiled_packages_dir(),
                            ctx.config.debug_packages_dir())

        if release:
            self.delta_search_paths[release] = search_paths
        elif max_count > 0:
            self.delta_history_search_paths.append((search_paths, max_count))

    def build_delta_packages(self, package):

        def find_old_package(filename, search_paths):
            for package_dir in search_paths:
                path = util.join_path(package_dir, filename)
                if os.path.exists(path):
                    return path
                else:
                    path = os.path.join(package_dir,
                                        util.parse_package_dir_path(filename),
                                        filename)
                    if os.path.exists(path):
                        return path

        old_packages = {}

        for old_release, search_paths in list(self.delta_search_paths.items()):
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
            if max_count < 1:
                continue

            found_old_packages = {}
            for update in self.spec.history[1:]:
                if update.release in old_packages:
                    continue

                filename = self.package_filename(package.metadata.package,
                                                 update)
                old_package = find_old_package(filename, search_paths)
                if old_package:
                    found_old_packages[update.release] = old_package

                    if len(found_old_packages) == max_count:
                        break

            old_packages.update(found_old_packages)

        from inary.operations.delta import create_delta_packages_from_obj
        return create_delta_packages_from_obj(list(old_packages.values()),
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
    except ActionScriptException as e:
        ctx.ui.error(_("Action script error caught. {}").format(e))
    finally:
        if ctx.ui.errors or ctx.ui.warnings:
            ctx.ui.warning(_("*** {} error(s), {} warning(s)").format(
                ctx.ui.errors, ctx.ui.warnings))
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
    ctx.ui.info(_("Last state was '{}'").format(last))

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
