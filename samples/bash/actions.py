#!/usr/bin/python
# -*- coding: utf-8 -*-

from pisi.actionsapi import gnuconfig
from pisi.actionsapi import autotools


def setup():
    gnuconfig.gnuconfig_update()
#    libtoolize.libtoolize()
    autotools.configure( '--with-nls' )

def build():
    autotools.make()

def install():
    autotools.install()
