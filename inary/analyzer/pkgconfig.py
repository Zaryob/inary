# -*- coding: utf-8 -*-
#
# Copyright (C) 2018, Suleyman POYRAZ (Zaryob)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#
"""dependency analyzer from pkgconfig .pc and .ldd files when package building"""

import os
import re
import sys
import glob
import magic
import shutil
import fnmatch
import tempfile
import optparse
import itertools
import subprocess

#Inary functions
import inary
import inary.context as ctx

#Gettext
import gettext
__trans = gettext.translation('inary', fallback=True)
_ = __trans.gettext

INSTALLDB = inary.db.installdb.InstallDB()
COMPONENTDB = inary.db.componentdb.ComponentDB()
CONSTANTS = inary.constants.Constants()
REPODB = inary.db.repodb.RepoDB()
FILESDB = inary.db.filesdb.FilesDB()

class Error(inary.Error):
    pass

class LDD:
    def __init__(self, packages, directory, component, installed_list=True, systembase=False, systemdevel=False):

        self.systembase = systembase
        self.systemdevel = systemdevel
        self.packages = package
        self.component = component

        # If directory is used as option
        if directory:
            for root, dirs, files in os.walk(directory):
                for data in files:
                    if data.endswith(".inary"):
                        self.packages.append(os.path.join(root, data))

        # check for components, like system.base, tex.language, etc.
        if self.component:
            for repo in RepoDB.list_repos():
                if COMPONENTDB.has_component(component):
                    self.packages.extend(COMPONENTDB.get_packages(component, repo))

        # check for all packages installed on the machine
        if installedlist:
            self.packages.extend(INSTALLDB.list_installed())

    def find_dependencies_on_pkgconfig(self):
        pkgconfig_list = []
        used_inary = False # Do not check for a inary binary file and for a package installed on the system
        for package in self.packages:
            # Check loop for .inary files
            if package.endswith(".inary"):
                used_inary = True
                package_inary = inary.package.Package(package)
                package_meta = package_inary.get_metadata()
                package_name = package_meta.package.name

                # Gather runtime dependencies directly from the metadata.xml
                package_deps = [dep.name() for dep in package_meta.package.runtimeDependencies()]

                # Contains extracted package content
                package_tempdir = tempfile.mkdtemp(prefix=os.path.basename(sys.argv[0]) + '-')
                package_inary.extract_install(package_tempdir)

                # Get results from objdump,ldd,etc...
                result_dependencies, result_broken, result_unused, result_undefined, result_runpath = \
                self.generate_result(package_name, package_tempdir)

                # Look for intersections of the packages(i.e. do not include system.base packages)
                # result_lists is a iteration object which contains tuples of length 3
                result_lists = self.check_intersections(result_dependencies, package_deps, package_name, self.systembase, self.systemdevel)

                # Delete the created temporary directory
                if package_tempdir.startswith("/tmp/"):
                    shutil.rmtree(package_tempdir)

                #add a touple 
                pkgconfig_list.append((result_broken, result_unused, result_undefined, result_lists, result_runpath, package_name))

            # Check for a installed package in the system
            elif package in INSTALLDB.list_installed():
                if used_inary:
                    raise Error("You've checked for a inary file before\nPlease do not check for a installed package and inary file at the same time")

                else:
                    package_name = package

                    # Gather runtime dependencies directly from the database of installed packages
                    package_deps = [dep.name() for dep in INSTALLDB.get_package(package).runtimeDependencies()]
                    package_tempdir = False # There is no need of temporary directory, hence we look for files that are installed

                    # Same functions in the above part. You can read them
                    result_dependencies, result_broken, result_unused, result_undefined, result_runpath = \
                    self.generate_result(package_name, package_tempdir)

                    result_lists = check_intersections(result_dependencies, package_deps, package_name, self.systembase, self.systemdevel)
                    pkgconfig_list.append((result_broken, result_unused, result_undefined, result_lists, result_runpath, package_name))

            else:
                raise Error("'{}' is not a valid .inary file or an installed package".format(package))

        return pkgconfig_list

    def process_ldd(self, objdump_needed, ldd_output, ldd_unused, ldd_undefined):
        '''Process the ldd outputs. And return a simple path only lists'''
        # result_needed = (all shared libary dependencies) - (needed shared library gathered from objdump)
        # result_broken = broken libraries that are not available at their place
        # result_unused = unused direct dependencies
        # result_undefined = undefined symbol errors
        result_unused = []
        result_undefined = []
        result_broken = []
        result_main_ldd = {}
        result_needed = []

        for line in ldd_unused.replace("\t", "").split("\n"):
            if not line == "" and not "Unused" in line:
                result_unused.append(line.strip())

        for line in ldd_undefined.replace("\t", "").split("\n"):
            if line.startswith("undefined symbol:"):
                result_undefined.append(re.sub("^undefined symbol: (.*)\((.*)\)$", "\\1", line))

        for line in ldd_output:
            if "=>" in line:
                # Filter these special objects
                if "linux-gate" in line or \
                        "ld-linux" in line or "linux-vdso" in line:
                    continue

                so_name, so_path = line.split("=>")
                if "not found" in so_path:
                    # One of the dynamic dependencies is missing
                    result_broken.append(so_name.strip())
                else:
                    result_main_ldd[so_name.strip()] = so_path.split(" (")[0].strip()

        for obj in objdump_needed:
            # Find the absolute path of libraries from their SONAME's
            if obj in result_main_ldd:
                result_needed.append(os.popen("readlink -f {}".format(result_main_ldd[obj]).read().strip()))
            else:
                result_needed.append(obj)

        return (result_needed, result_broken, result_unused, result_undefined)

    def check_objdump(self, processed_needed, package_elf_files, package_name):
        '''check the objdump needed libraries with the ldd libraries
        the libraries that are needed can be used for dependencies'''
        result_needed = []
        # check  if the libraries are shipped with the package
        # then associate each library(with his package_name)  with the given elf_file
        for obj in processed_needed:
            if obj_dump in package_elf_files:
                # file is shipped within this package
                dependency_name = package_name
            else:
                # search for the package name (i.e: inary sf /usr/lib/*.so )
                # the library may not exist, thus adding an exception is welcome
                try:
                    dependency_name = inary.api.search_file(obj_dump)[0][0]
                except IndexError:
                    dependency_name = "broken"
                    ctx.ui.info("{} (probably broken dependency)".format(needed))
            result_needed.append((obj_dump, dependency_name))
        return result_needed

    def check_pc_files(self, pc_file):
        '''check for .pc files created by pkgconfig and shipped with the package
           these .pc files have requirements tags that can be used for dependencies'''
        result_needed = []
        requires = set(os.popen("pkg-config --print-requires --print-requires-private {} | gawk '{ print $1 }'".format(
                os.path.basename(pc_file).replace(".pc", ""))).read().split("\n")[:-1])

        for require in requires:
            require_file = "/usr/share/pkgconfig/{}.pc".format(require)

            if not os.path.exists(require_file):
                require_file = "/usr/lib/pkgconfig/{}.pc".format(require)
            try:
                dependency_name = inary.api.search_file(require_file)[0][0]
            except IndexError:
                dependency_name = "broken"

            result_needed.append((require_file, dependency_name))

        return result_needed

    def check_intersections(self, result_dependencies, package_deps, package_name):
        '''eliminate system base and system devel packages and self written deps'''

        # get system.base and system.devel packages
        systembase_packages = []
        systemdevel_packages= []
        for repo in REPODB.list_repos():
            for component in COMPONENTDB.list_components(repo):
                if component == "system.base":
                    systembase_packages.extend(COMPONENTDB.get_packages('system.base', repo))
                if component == "system.devel":
                    systemdevel_packages.extend(COMPONENTDB.get_packages('system.devel', repo))

        # look for packages that are system.base but are written as dependency
        # mark them with "*"
        result_must_removed = list(set(package_deps) & set(systembase_packages))
        for deps in package_deps:
            if deps in result_must_removed:
                package_deps[package_deps.index(deps)] = "{} (base)".format(deps)

        # look for packages that are system.devel but are written as dependency
        # mark them with "*"
        result_must_removed = list(set(package_deps) & set(systemdevel_packages))
        for deps in package_deps:
            if deps in result_must_removed:
                package_deps[package_deps.index(deps)] = "{} (devel)".format(deps)

        # extract the dependency package names and store them in result_deps
        # dependencies tagged as broken or given itself are eliminated
        dependencies = set()
        result_deps = []
        for elf_files, paths_and_deps in list(result_dependencies.items()):
            for data in paths_and_deps:
                if not data[1] == "broken" and not data[1] == package_name:
                    result_deps.append(data[1])

        # remove packages that belong to system.base component
        if not self.systembase:
            result_deps = list(set(result_deps) - set(systembase_packages))
        if not self.systemdevel and package_name.endswith('-devel'):
            result_deps = list(set(result_deps) - set(systemdevel_packages))
        if self.systemdevel or self.systembase:
            result_must_removed = list(set(result_deps) & set(systembase_packages))
            for deps in result_deps:
                if deps in result_must_removed:
                    result_deps[result_deps.index(deps)] = "{} (base)".format(deps)
            result_must_removed = list(set(result_deps) & set(systemdevel_packages))
            for deps in result_deps:
                if deps in result_must_removed:
                    result_deps[result_deps.index(deps)] = "{} (devel)".format(deps)
            result_deps = list(set(result_deps))

        # remove packages that already are written in metadata.xml (runtime dependencies written in pspec.xml)
        result_section = list(set(result_deps) -  set(package_deps))

        # create a sorted iteration object of the final results variables
        # the lists may have variable lengths, thus we fill the smallers one with empty strings.
        key_func = lambda x: len(x)
        result_lists = itertools.zip_longest(sorted(list(set(package_deps)), key=key_func),
                                             sorted(result_deps, key=key_func),
                                             sorted(result_section, key=key_func),
                                             fillvalue="")
        return result_lists

    def generate_result(self, package_name, package_dir):
        '''execute ldd on elf files and returns them'''

        #There maybe more than one elf file, check for each one
        _dependencies = {}
        _unused = {}
        _undefined = {}
        _broken = None
        _runpath = {}
        ld_library_paths = set()

        package_elf_files = []

        # Two options are available. Checking for a inary file or an installed package in the database
        if package_dir:
            package_files = os.popen("find {}".format(package_dir)).read().strip().split("\n")
            package_pc_files = glob.glob("{}/usr/*/pkgconfig/*.pc".format(package_dir))
        else:
            package_files = set(["/{}".format(file_name.path) \
                for file_name in INSTALLDB.get_files(package_name).list])
            package_pc_files = set([os.path.realpath("/{}".format(file_name.path)) \
                    for file_name in INSTALLDB.get_files(package_name).list \
                    if fnmatch.fnmatch(file_name.path, "*/pkgconfig/*.pc")])

        for package_file in package_files:
            package_file_info = magic.from_file(package_file) #Return file type
            if "LSB shared object" in package_file_info:
                package_elf_files.append(os.path.realpath(package_file))
            elif "LSB executable" in package_file_info:
                package_elf_files.append(package_file)

        # Add library paths for unpacked inary files
        if package_dir:
            for elf_file in package_elf_files:
                if elf_file.endswith(".so") or ".so." in elf_file:
                    ld_library_paths.add(os.path.dirname(elf_file))
            os.environ.update({'LD_LIBRARY_PATH': ":".join(ld_library_paths)})

        for elf_file in package_elf_files:
            ldd_output = str(subprocess.Popen(["ldd", elf_file],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT,
                                              env = os.environ).communicate()[0]).strip().split("\n")

            ldd_unused = str(subprocess.Popen(["ldd", "-u", "-r", elf_file],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              env = os.environ).communicate()[0])

            ldd_undefined = str(subprocess.Popen(["ldd", "-u", "-r", elf_file],
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE,
                                                 env = os.environ).communicate()[1])


            runpath  = str(subprocess.Popen(["chrpath", "-l", elf_file],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            env = os.environ).communicate()[0]).strip().split(": ")

            objdump_needed = [line.strip().split()[1] for line in \
                    os.popen("objdump -p \"{}\" | grep 'NEEDED'".format(elf_file)).readlines()]


            # Process the various ldd and objdump outputs
            processed_needed, processed_broken, processed_unused, processed_undefined = \
            self.process_ldd(objdump_needed, ldd_output, ldd_unused, ldd_undefined)

            # association with each single elf file
            _unused.update(dict([(elf_file, processed_unused)]))
            _undefined.update(dict([(elf_file, processed_undefined)]))
            _runpath.update(dict([(elf_file, runpath)]))
            _broken = processed_broken
            _dependencies[elf_file] =  self.check_objdump(processed_needed, package_elf_files, package_name)

        # Check for .pc files
        for pc_file in package_pc_files:
            _dependencies[pc_file] = check_pc_files(pc_file)

        return (_dependencies, _broken, _unused, _undefined, _runpath)


