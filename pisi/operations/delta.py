# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os

import gettext
__trans = gettext.translation("pisi", fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
import pisi.package
import pisi.util as util
import pisi.archive as archive


# FIXME Reduce code duplication
def create_delta_packages_from_obj(old_packages, new_package_obj, specdir):
    new_pkg_info = new_package_obj.metadata.package
    new_pkg_files = new_package_obj.files

    new_pkg_path = new_package_obj.tmp_dir

    new_pkg_name = os.path.basename(new_package_obj.filepath)
    name, new_version, new_release, new_distro_id, new_arch = \
            util.split_package_filename(new_pkg_name)

    cwd = os.getcwd()
    out_dir = ctx.get_option("output_dir")
    target_format = ctx.get_option("package_format")
    delta_packages = []

    for old_package in old_packages:
        old_pkg = pisi.package.Package(old_package)
        old_pkg_info = old_pkg.metadata.package

        delta_name = "-".join((old_pkg_info.name,
                               old_pkg_info.release,
                               new_pkg_info.release,
                               new_distro_id,
                               new_arch)) + ctx.const.delta_package_suffix

        ctx.ui.info(_("Creating %s...") % delta_name)

        if out_dir:
            delta_name = util.join_path(out_dir, delta_name)

        old_pkg_files = old_pkg.get_files()

        delta_pkg = pisi.package.Package(delta_name, "w", format=target_format)

        # add comar files to package
        os.chdir(specdir)
        for pcomar in new_pkg_info.providesComar:
            fname = util.join_path(ctx.const.comar_dir, pcomar.script)
            delta_pkg.add_to_package(fname)

        # add xmls and files
        os.chdir(new_pkg_path)

        delta_pkg.add_metadata_xml(ctx.const.metadata_xml)
        delta_pkg.add_files_xml(ctx.const.files_xml)

        files_delta = find_delta(old_pkg_files, new_pkg_files)

        # only metadata information may change in a package,
        # so no install archive added to delta package
        if files_delta:
            # Sort the files in-place according to their path for an ordered
            # tarfile layout which dramatically improves the compression
            # performance of lzma. This improvement is stolen from build.py
            # (commit r23485).
            files_delta.sort(key=lambda x: x.path)

            for finfo in files_delta:
                orgname = util.join_path("install", finfo.path)
                if new_pkg_info.debug_package:
                    orgname = util.join_path("debug", finfo.path)
                delta_pkg.add_to_install(orgname, finfo.path)

        os.chdir(cwd)

        delta_pkg.close()
        delta_packages.append(delta_name)

    # Return delta package names
    return delta_packages

def create_delta_packages(old_packages, new_package):
    if new_package in old_packages:
        ctx.ui.warning(_("New package '%s' exists in the list of old "
                         "packages. Skipping it...") % new_package)
        while new_package in old_packages:
            old_packages.remove(new_package)

    new_pkg = pisi.package.Package(new_package)
    new_pkg_info = new_pkg.metadata.package
    new_pkg_files = new_pkg.get_files()

    # Unpack new package to temp
    new_pkg_name = os.path.splitext(os.path.basename(new_package))[0]

    new_pkg_path = util.join_path(ctx.config.tmp_dir(), new_pkg_name)
    new_pkg.extract_pisi_files(new_pkg_path)
    new_pkg.extract_dir("comar", new_pkg_path)

    install_dir = util.join_path(new_pkg_path, "install")
    util.clean_dir(install_dir)
    os.mkdir(install_dir)
    new_pkg.extract_install(install_dir)

    name, new_version, new_release, new_distro_id, new_arch = \
            util.split_package_filename(new_pkg_name)

    cwd = os.getcwd()
    out_dir = ctx.get_option("output_dir")
    target_format = ctx.get_option("package_format")
    delta_packages = []

    for old_package in old_packages:
        old_pkg = pisi.package.Package(old_package)
        old_pkg_info = old_pkg.metadata.package

        if old_pkg_info.name != new_pkg_info.name:
            ctx.ui.warning(_("The file '%s' belongs to a different package "
                             "other than '%s'. Skipping it...")
                             % (old_package, new_pkg_info.name))
            continue

        if old_pkg_info.release == new_pkg_info.release:
            ctx.ui.warning(_("Package '%s' has the same release number with "
                             "the new package. Skipping it...") % old_package)
            continue

        delta_name = "-".join((old_pkg_info.name,
                               old_pkg_info.release,
                               new_pkg_info.release,
                               new_distro_id,
                               new_arch)) + ctx.const.delta_package_suffix

        ctx.ui.info(_("Creating %s...") % delta_name)

        if out_dir:
            delta_name = util.join_path(out_dir, delta_name)

        old_pkg_files = old_pkg.get_files()

        delta_pkg = pisi.package.Package(delta_name, "w", format=target_format)

        os.chdir(new_pkg_path)

        # add comar files to package
        for pcomar in new_pkg_info.providesComar:
            fname = util.join_path(ctx.const.comar_dir, pcomar.script)
            delta_pkg.add_to_package(fname)

        # add xmls and files
        delta_pkg.add_metadata_xml(ctx.const.metadata_xml)
        delta_pkg.add_files_xml(ctx.const.files_xml)

        files_delta = find_delta(old_pkg_files, new_pkg_files)

        # only metadata information may change in a package,
        # so no install archive added to delta package
        if files_delta:
            # Sort the files in-place according to their path for an ordered
            # tarfile layout which dramatically improves the compression
            # performance of lzma. This improvement is stolen from build.py
            # (commit r23485).
            files_delta.sort(key=lambda x: x.path)

            os.chdir(install_dir)
            for f in files_delta:
                delta_pkg.add_to_install(f.path)

        os.chdir(cwd)

        delta_pkg.close()
        delta_packages.append(delta_name)

    # Remove temp dir
    util.clean_dir(new_pkg_path)

    # Return delta package names
    return delta_packages

def create_delta_package(old_package, new_package):
    packages = create_delta_packages([old_package], new_package)
    return packages or None


#  Hash not equals                      (these are the deltas)
#  Hash equal but path different ones   (these are the relocations)
#  Hash and also path equal ones        (do nothing)

def find_delta(old_files, new_files):

    hashto_files = {}
    for f in new_files.list:
        hashto_files.setdefault(f.hash, []).append(f)

    new_hashes = set([f.hash for f in new_files.list])
    old_hashes = set([f.hash for f in old_files.list])
    hashes_delta = new_hashes - old_hashes

    deltas = []
    for h in hashes_delta:
        deltas.extend(hashto_files[h])

    # Directory hashes are None. There was a bug with PolicyKit that
    # should have an empty directory.
    if None in hashto_files:
        deltas.extend(hashto_files[None])

    return deltas

def find_relocations(oldfiles, newfiles):

    files_new = {}
    for f in newfiles.list:
        files_new.setdefault(f.hash, []).append(f)

    files_old = {}
    for f in oldfiles.list:
        files_old.setdefault(f.hash, []).append(f)

    relocations = []
    for h in files_new.keys():
        if h and h in files_old:
            old_paths = [x.path for x in files_old[h]]
            for i in range(len(files_new[h])):
                if files_new[h][i].path not in old_paths:
                    relocations.append((files_old[h][0], files_new[h][i]))

    return relocations

def find_permission_changes(oldfiles, newfiles):

    files_new = {}
    for f in newfiles.list:
        files_new.setdefault(f.hash, []).append(f)

    for old_file in oldfiles.list:
        files = files_new.get(old_file.hash, [])

        for _file in files:
            if old_file.mode == _file.mode:
                continue

            path = os.path.join(ctx.config.dest_dir(), _file.path)
            if os.path.exists(path):
                yield path, int(_file.mode, 8)
