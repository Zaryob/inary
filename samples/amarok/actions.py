#!/usr/bin/python
# -*- coding: utf-8 -*-

from pisi.actionsapi import gnuconfig
from pisi.actionsapi import kde

def setup():
    gnuconfig.gnuconfig_update()

    # amarok does not respect kde coding standards, and makes a lot of
    # assuptions regarding its installation directory. For this reason,
    # it must be installed in the KDE install directory.
    kde.configure('--with-arts --with-xine --with-gstreamer --with-opengl --with-libvisual --disable-amazon --disable-debug --without-debug')

def build():
    kde.make()

def install():
    kde.install()
