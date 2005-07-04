#!/usr/bin/python
# -*- coding: utf-8 -*-

from pisi.actionsapi import gnuconfig
from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools


def setup():
    gnuconfig.gnuconfig_update()

    pisitools.dosed("configure", "s:-lcurses:-lncurses:")

    autotools.configure("--with-nls --disable-profiling --without-gnu-malloc")

    pisitools.dosed("Makefile", "/^TERMCAP_LIB/s:-lncurses:-Wl,-Bstatic -lncurses -Wl,-Bdynamic:")

def build():
    autotools.make()

def install():
    autotools.install()
