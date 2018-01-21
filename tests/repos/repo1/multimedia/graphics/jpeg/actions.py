#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Suleyman POYRAZ (Zaryob)
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

from inary.actionsapi import autotools
from inary.actionsapi import inarytools
from inary.actionsapi import libtools
from inary.actionsapi import get
from inary.actionsapi import shelltools

def setup():
    autotools.autoreconf("-vfi")
    options = "--enable-shared \
               --disable-static \
               --enable-maxmem=64 \
               --disable-dependency-tracking"

    if get.buildTYPE() == "emul32":
        options += " --prefix=/emul32 --libdir=/usr/lib32"
        shelltools.export("CFLAGS", "%s -m32" % get.CFLAGS())

    autotools.configure(options)

def build():
    autotools.make()

def install():
    autotools.rawInstall('DESTDIR="%s"' % get.installDIR())

    if get.buildTYPE() == "emul32":
        inarytools.removeDir("/emul32")
        return

    # they say some programs use this
    inarytools.insinto("/usr/include", "jpegint.h")
    inarytools.insinto("/usr/include", "jinclude.h")

    inarytools.dodoc("change.log", "example.c", "README","*.txt")

