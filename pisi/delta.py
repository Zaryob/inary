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
__trans = gettext.translation('pisi', fallback=True)
_ = __trans.ugettext

import pisi.context as ctx
from pisi.package import Package
import pisi.util as util
import pisi.archive as archive

def create_delta_package(old_package, new_package):

    oldpkg = Package(old_package, "r")
    newpkg = Package(new_package, "r")

    newmd = newpkg.get_metadata()
    oldmd = oldpkg.get_metadata()

    oldfiles = oldpkg.get_files()
    newfiles = newpkg.get_files()

    files_delta = find_delta(oldfiles, newfiles)

    # FIXME: handle only metadata changed cases
    if not files_delta:
        ctx.ui.info(_("Nothing has changed between builds, not creating a delta"))
        return

    ctx.ui.info(_("Creating delta PiSi package between %s %s") % (old_package, new_package))

    # Unpack new package to temp
    newpkg_name = util.package_name(newmd.package.name, newmd.package.version, newmd.package.release, newmd.package.build, False)
    newpkg_path = util.join_path(ctx.config.tmp_dir(), newpkg_name)
    newpkg.extract_to(newpkg_path, True)

    tar = archive.ArchiveTar(util.join_path(newpkg_path, ctx.const.install_tar_lzma), 'tarlzma', False, False)
    tar.unpack_dir(newpkg_path)

    # symlinks should be in delta package
    symlinks = filter(lambda x:os.path.islink(util.join_path(newpkg_path, x.path)), newfiles.list)
    files_delta = set(files_delta + symlinks)

    # Create delta package
    deltaname = "%s-%s-%s%s" % (oldmd.package.name, oldmd.package.release, newmd.package.release, ".delta.pisi")
    
    outdir = ctx.get_option('output_dir')
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

    ctx.build_leftover = util.join_path(ctx.config.tmp_dir(), ctx.const.install_tar_lzma)

    tar = archive.ArchiveTar(util.join_path(ctx.config.tmp_dir(), ctx.const.install_tar_lzma), "tarlzma")
    for file in files_delta:
        tar.add_to_archive(file.path)
    tar.close()

    os.chdir(ctx.config.tmp_dir())
    deltapkg.add_to_package(ctx.const.install_tar_lzma)
    deltapkg.close()

    os.unlink(util.join_path(ctx.config.tmp_dir(), ctx.const.install_tar_lzma))
    ctx.build_leftover = None
    os.chdir(c)

    ctx.ui.info(_("Done."))

#  Hash not equals                      (these are the deltas)
#  Hash equal but path different ones   (these are the relocations)
#  Hash and also path equal ones        (do nothing)

def find_delta(oldfiles, newfiles):

    hashto_files = {}
    for file in newfiles.list:
        files_new.setdefault(file.hash, []).append(file)

    files_new = set(map(lambda x:x.hash, newfiles.list))
    files_old = set(map(lambda x:x.hash, oldfiles.list))
    files_delta = files_new - files_old

    return map(lambda x:hashto_files[x][0], files_delta)

def find_relocations(oldfiles, newfiles):

# FIXME: A minor issue: Hash files may collide in any package (same file in different 
# places in the same package.. ex. COPYING). Handle this case if check fails while installing. 
# Because of that we do not use sets here but lists to append those files.

    files_new = {}
    for file in newfiles.list:
        files_new.setdefault(file.hash, []).append(file)

    files_old = {}
    for file in oldfiles.list:
        files_old.setdefault(file.hash, []).append(file)

    relocations = []
    for hash in files_new.keys():
        if hash in files_old and files_new[hash][0].path != files_old[hash][0].path:
            # symlinks are not relocated, they already come with the delta package
            if not os.path.islink("/" + files_old[hash][0].path):
                relocations.append((files_old[hash][0], files_new[hash][0]))

    return relocations
