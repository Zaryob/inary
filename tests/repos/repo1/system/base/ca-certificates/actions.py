#!/usr/bin/python
# -*- coding: utf-8 -*-
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt

from inary.actionsapi import get
from inary.actionsapi import autotools
from inary.actionsapi import inarytools
from inary.actionsapi import shelltools


def build():
    autotools.make("SUBDIRS=mozilla")


def install():
    inarytools.dodir("usr/share/ca-certificates/mozilla")
    inarytools.dodir("usr/sbin")

    autotools.install("SUBDIRS=mozilla DESTDIR=%s" % get.installDIR())
    inarytools.doman("sbin/update-ca-certificates.8")

    shelltools.cd("%s/usr/share/ca-certificates" % get.installDIR())
    shelltools.system("find . -name '*.crt' | sort | cut -b3- > ca-certificates.conf")
    inarytools.insinto("/etc/", "ca-certificates.conf")

    inarytools.dodir("/etc/ca-certificates/update.d")
    inarytools.dodir("etc/ssl/certs")
