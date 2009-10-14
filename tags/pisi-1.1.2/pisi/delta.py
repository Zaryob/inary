# -*- coding: utf-8 -*-
#
# Copyright (C) 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
from sets import Set as set

import gettext
__trans = gettext.translation("pisi", fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
from pisi.package import Package
import pisi.util as util
import pisi.archive as archive

def create_delta_package(old_package, new_package):

    if old_package == new_package:
        ctx.ui.error(_("Cannot create delta for same package!"))
        return

    oldpkg = Package(old_package, "r")
    newpkg = Package(new_package, "r")

    newmd = newpkg.get_metadata()
    oldmd = oldpkg.get_metadata()

    oldfiles = oldpkg.get_files()
    newfiles = newpkg.get_files()

    files_delta = find_delta(oldfiles, newfiles)

    ctx.ui.info(_("Creating delta PiSi package between %s %s") % (old_package, new_package))

    # Unpack new package to temp
    newpkg_name = util.package_name(newmd.package.name, newmd.package.version, newmd.package.release, newmd.package.build, False)
    newpkg_path = util.join_path(ctx.config.tmp_dir(), newpkg_name)
    newpkg.extract_to(newpkg_path, True)

    tar = archive.ArchiveTar(util.join_path(newpkg_path, ctx.const.install_tar_lzma), "tarlzma", False, False)
    tar.unpack_dir(newpkg_path)

    # Create delta package
    deltaname = "%s-%s-%s%s" % (oldmd.package.name, oldmd.package.build, newmd.package.build, ctx.const.delta_package_suffix)

    outdir = ctx.get_option("output_dir")
    if outdir:
        deltaname = util.join_path(outdir, deltaname)

    deltapkg = Package(deltaname, "w")

    c = os.getcwd()
    os.chdir(newpkg_path)

    # add comar files to package
    for pcomar in newmd.package.providesComar:
        fname = util.join_path(ctx.const.comar_dir, pcomar.script)
        deltapkg.add_to_package(fname)

    # add xmls and files
    deltapkg.add_to_package(ctx.const.metadata_xml)
    deltapkg.add_to_package(ctx.const.files_xml)

    # only metadata information may change in a package, so no install.tar.lzma added to delta package
    if files_delta:
        ctx.build_leftover = util.join_path(ctx.config.tmp_dir(), ctx.const.install_tar_lzma)

        tar = archive.ArchiveTar(util.join_path(ctx.config.tmp_dir(), ctx.const.install_tar_lzma), "tarlzma")
        for file in files_delta:
            tar.add_to_archive(file.path)
        tar.close()

        os.chdir(ctx.config.tmp_dir())
        deltapkg.add_to_package(ctx.const.install_tar_lzma)

    deltapkg.close()

    tmp_file = util.join_path(ctx.config.tmp_dir(), ctx.const.install_tar_lzma)
    if os.path.exists(tmp_file):
        os.unlink(tmp_file)

    ctx.build_leftover = None
    os.chdir(c)

    ctx.ui.info(_("Done."))

#  Hash not equals                      (these are the deltas)
#  Hash equal but path different ones   (these are the relocations)
#  Hash and also path equal ones        (do nothing)

def find_delta(oldfiles, newfiles):

    hashto_files = {}
    for file in newfiles.list:
        hashto_files.setdefault(file.hash, []).append(file)

    files_new = set(map(lambda x:x.hash, newfiles.list))
    files_old = set(map(lambda x:x.hash, oldfiles.list))
    files_delta = files_new - files_old

    deltas = []
    for hash in files_delta:
        deltas.extend(hashto_files[hash])

    return deltas

def find_relocations(oldfiles, newfiles):

    files_new = {}
    for file in newfiles.list:
        files_new.setdefault(file.hash, []).append(file)

    files_old = {}
    for file in oldfiles.list:
        files_old.setdefault(file.hash, []).append(file)

    relocations = []
    for hash in files_new.keys():
        if hash and hash in files_old:
            for i in range(len(files_new[hash])):
                if files_old[hash][0].path != files_new[hash][i].path:
                    relocations.append((files_old[hash][0], files_new[hash][i]))

    return relocations
