#!/usr/bin/python
# -*- coding: utf-8 -*-

import pisi.actionsapi.gnuconfig as gnuconfig
import pisi.actionsapi.libtoolize as libtoolize
import pisi.actionsapi.autotools as autotools

def setup():
    gnuconfig.gnuconfig_update()
#    libtoolize.libtoolize()
    autotools.configure( '--with-nls' )

def build():
    autotools.make()

def install():
    autotools.install()
