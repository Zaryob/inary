# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2010, TUBITAK/UEKAE
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


def create_delta_package(old_package, new_package):

    if old_package == new_package:
        ctx.ui.error(_("Cannot create delta for same package!"))
        return

    oldpkg = pisi.package.Package(old_package, "r")
    newpkg = pisi.package.Package(new_package, "r")

    newmd = newpkg.metadata
    oldmd = oldpkg.metadata

    oldfiles = oldpkg.get_files()
    newfiles = newpkg.get_files()

    files_delta = find_delta(oldfiles, newfiles)

    ctx.ui.info(_("Creating delta PiSi package between %s %s")
                % (old_package, new_package))

    # Unpack new package to temp
    newpkg_name = util.package_name(newmd.package.name,
                                    newmd.package.version,
                                    newmd.package.release,
                                    newmd.package.build,
                                    False)
    newpkg_path = util.join_path(ctx.config.tmp_dir(), newpkg_name)
    newpkg.extract_pisi_files(newpkg_path)
    newpkg.extract_dir("comar", newpkg_path)

    install_dir = util.join_path(newpkg_path, "install")
    util.clean_dir(install_dir)
    os.mkdir(install_dir)
    newpkg.extract_install(install_dir)

    # Create delta package
    deltaname = "%s-%s-%s%s" % (oldmd.package.name,
                                oldmd.package.build,
                                newmd.package.build,
                                ctx.const.delta_package_suffix)

    outdir = ctx.get_option("output_dir")
    if outdir:
        deltaname = util.join_path(outdir, deltaname)

    deltapkg = pisi.package.Package(deltaname, "w",
                                    format=ctx.get_option("package_format"))

    c = os.getcwd()
    os.chdir(newpkg_path)

    # add comar files to package
    for pcomar in newmd.package.providesComar:
        fname = util.join_path(ctx.const.comar_dir, pcomar.script)
        deltapkg.add_to_package(fname)

    # add xmls and files
    deltapkg.add_metadata_xml(ctx.const.metadata_xml)
    deltapkg.add_files_xml(ctx.const.files_xml)

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
            deltapkg.add_to_install(f.path)

    deltapkg.close()

    os.chdir(c)

    # Remove temp dir
    util.clean_dir(newpkg_path)

    ctx.ui.info(_("Done."))

    # return delta package name
    return deltaname


#  Hash not equals                      (these are the deltas)
#  Hash equal but path different ones   (these are the relocations)
#  Hash and also path equal ones        (do nothing)

def find_delta(oldfiles, newfiles):

    hashto_files = {}
    for f in newfiles.list:
        hashto_files.setdefault(f.hash, []).append(f)

    files_new = set(map(lambda x: x.hash, newfiles.list))
    files_old = set(map(lambda x: x.hash, oldfiles.list))
    files_delta = files_new - files_old

    deltas = []
    for h in files_delta:
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
