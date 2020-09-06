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

# Standart Python Libraries
import os

# Inary Modules
import inary.package
import inary.util as util
import inary.context as ctx

# Gettext Library
import gettext
__trans = gettext.translation("inary", fallback=True)
_ = __trans.gettext


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
        old_pkg = inary.package.Package(old_package)
        old_pkg_info = old_pkg.metadata.package

        if old_pkg_info.name != new_pkg_info.name:
            ctx.ui.warning(
                _("The file \"{0}\" belongs to a different package other than '{1}'. Skipping it...").format(old_package,
                                                                                                             new_pkg_info.name))
            continue

        if old_pkg_info.release == new_pkg_info.release:
            ctx.ui.warning(
                _("Package \"{}\" has the same release number with the new package. Skipping it...").format(old_package))
            continue

        delta_name = "-".join((old_pkg_info.name,
                               old_pkg_info.release,
                               new_pkg_info.release,
                               new_distro_id,
                               new_arch)) + ctx.const.delta_package_suffix

        ctx.ui.info(_("Creating delta package: \"{}\"...").format(delta_name))

        if out_dir:
            delta_name = util.join_path(out_dir, delta_name)

        old_pkg_files = old_pkg.get_files()

        files_delta = find_delta(old_pkg_files, new_pkg_files)

        if len(files_delta) == len(new_pkg_files.list):
            ctx.ui.warning(_(
                "All files in the package \"{}\" are different from the files in the new package. Skipping it...").format(
                old_package))
            continue

        delta_pkg = inary.package.Package(
            delta_name, "w", format=target_format)

        # add postops files to package
        os.chdir(specdir)
        for postops in ctx.const.postops:
            try:
                delta_pkg.add_to_package(ctx.const.postops)
            except:
                pass

        # add xmls and files
        os.chdir(new_pkg_path)

        delta_pkg.add_metadata_xml(ctx.const.metadata_xml)
        delta_pkg.add_files_xml(ctx.const.files_xml)

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
        ctx.ui.warning(
            _("New package \"{}\" exists in the list of old packages. Skipping it...").format(new_package))
        while new_package in old_packages:
            old_packages.remove(new_package)

    new_pkg_name = os.path.splitext(os.path.basename(new_package))[0]
    new_pkg_path = util.join_path(ctx.config.tmp_dir(), new_pkg_name)

    new_pkg = inary.package.Package(new_package, tmp_dir=new_pkg_path)
    new_pkg.read()

    # Unpack new package to temp
    new_pkg.extract_inary_files(new_pkg_path)
    try:
        new_pkg.extract_file(ctx.const.postops, new_pkg_path)
    except BaseException:
        pass

    install_dir = util.join_path(new_pkg_path, "install")
    util.clean_dir(install_dir)
    os.mkdir(install_dir)
    new_pkg.extract_install(install_dir)

    delta_packages = create_delta_packages_from_obj(old_packages,
                                                    new_pkg,
                                                    new_pkg_path)

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
    hashes_delta = list(new_hashes - old_hashes)

    # Add to-be-replaced config files to delta package regardless of its state
    hashes_delta.extend(
        [f.hash for f in new_files.list if f.type == 'config' and f.replace])

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
    for h in list(files_new.keys()):
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
