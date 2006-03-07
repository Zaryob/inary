#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.

#
#  Build edilmiş bir pspec.xml dosyası içerisinden çıkan tüm paketlerin kapsadığı tüm
# dosyalar ile install dizini altında oluşan dosyaları kontrol ederek paketlerin
# hiç birisine girmeyen dosya varsa bulur ve gösterir..
#
#  #2225'teki iyileştirme önerisine istinaden..
#

import sys
import os

from pisi.specfile import SpecFile
import pisi.context as ctx
import pisi.util as util

def pisi_init():
    import pisi.config
    ctx.config = pisi.config.Config()
    ctx.initialized = True

def pisi_finalize():
    ctx.initialized = False

def pkg_dir(spec):
    packageDir = spec.source.name + '-' + spec.source.version + '-' + spec.source.release
    return util.join_path(ctx.config.dest_dir(), ctx.config.values.dirs.tmp_dir, packageDir)
 
def main():
    pisi_init()

    spec = SpecFile()

    try:
        spec.read(sys.argv[1], ctx.config.tmp_dir())
    except:
        print "'%s' geçerli bir pspec.xml dosyası değil.." % (sys.argv[1])
        return

    package_dir = pkg_dir(spec)
    install_dir = util.join_path(package_dir + ctx.const.install_dir_suffix)

    if not os.path.isdir(install_dir):
        print "'%s' dizini yok. Paket build edilmemiş olabilir.." % (install_dir)
        return

    all_paths_in_packages = []
    all_files_under_install_dir = []
    files_already_in_any_package = []

    for package in spec.packages:
        for path in package.files:
            all_paths_in_packages.append(util.join_path(install_dir + path.path))

    for r, d, f in os.walk(install_dir):
        for fi in f:
            all_files_under_install_dir.append(util.join_path(r, fi))

    for file_ in all_files_under_install_dir:
        for path_ in all_paths_in_packages:
            if not file_.find(path_):
                files_already_in_any_package.append(file_)

    unowned_files = set(all_files_under_install_dir) - set(files_already_in_any_package)

    if unowned_files:
        print
        print "Install dizininde oluşmuş fakat pspec.xml içerisindeki hiç bir pakete dahil edilmemiş dosyalar:"
        print "==============================================================================================="
        print
        for p in unowned_files:
            print p
        print

    else:
        print "Install dizininde oluşmuş fakat pspec.xml içerisindeki hiç bir pakete dahil edilmemiş dosya yok"

    pisi_finalize()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main()
    else:
        print "Parametre olarak pspec.xml dosyası vermelisiniz.."
